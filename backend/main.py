"""
FastAPI application — main entry point.
Serves the API + orchestrates the full marketing pipeline.
"""

import os
from dotenv import load_dotenv
load_dotenv()  # Load .env BEFORE any module reads os.getenv()

import json
import uuid
import asyncio
from datetime import datetime, date, timedelta
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from loguru import logger

from config import settings
from storage.database import init_db, get_session_direct, ScrapedContent, Campaign, CreativeAsset, AgentLog, PipelineRun, AnalysisResult, APIBudget
from company_profile import CompanyProfile

# Lazy imports — these modules have heavy deps (chromadb, transformers, etc.)
# The backend starts fine without them; features degrade gracefully.
EmbeddingStore = None
try:
    from storage.embeddings import EmbeddingStore
except ImportError:
    logger.warning("chromadb/sentence-transformers not installed — vector search disabled")

try:
    from scrapers.youtube import YouTubeScraper
    from scrapers.tiktok import TikTokScraper
    from scrapers.news import NewsScraper
    from scrapers.google_trends import GoogleTrendsScraper
    from scrapers.reddit import RedditScraper
    from scrapers.twitter import TwitterScraper
    from scrapers.competitor import CompetitorScraper
    from scrapers.memes import MemeScraper
except ImportError as e:
    logger.warning(f"Scraper import failed: {e}")
    # Ensure all scraper names exist for graceful degradation
    YouTubeScraper = None
    TikTokScraper = None
    NewsScraper = None
    GoogleTrendsScraper = None
    RedditScraper = None
    TwitterScraper = None
    CompetitorScraper = None
    MemeScraper = None

try:
    from analysis.pipeline import AnalysisPipeline
except ImportError:
    logger.warning("Analysis pipeline deps not installed — analysis disabled")
    AnalysisPipeline = None

from agents.router import LLMRouter
from agents.council import AgentCouncil

try:
    from creative.video_gen import VideoGenerator
    from creative.brief_gen import BriefGenerator
except ImportError:
    logger.warning("Creative deps not installed — video/brief gen disabled")
    VideoGenerator = None
    BriefGenerator = None

try:
    from notifications.dispatcher import NotificationDispatcher
except ImportError:
    logger.warning("Notification deps not installed")
    NotificationDispatcher = None

try:
    from scheduler.jobs import PipelineScheduler
except ImportError:
    logger.warning("Scheduler deps not installed")
    PipelineScheduler = None

from sqlalchemy import select, func, desc

# ── Globals ───────────────────────────────────────────────
embedding_store: Optional[EmbeddingStore] = None
pipeline_scheduler: Optional[PipelineScheduler] = None
llm_router: Optional[LLMRouter] = None
notifier: Optional[NotificationDispatcher] = None
company_profile: Optional[CompanyProfile] = None

PIPELINE_PROGRESS = {}
STREAM_QUEUES = {}

# ── Lifespan ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global embedding_store, pipeline_scheduler, llm_router, notifier, company_profile

    # Startup
    logger.info("Starting Marketing Automation Platform...")
    os.makedirs("./data", exist_ok=True)
    os.makedirs("./data/outputs", exist_ok=True)

    await init_db(settings.database_url)

    if EmbeddingStore:
        try:
            embedding_store = EmbeddingStore(settings.chroma_persist_dir)
        except Exception as e:
            logger.warning(f"EmbeddingStore init failed: {e}")

    company_profile = CompanyProfile()
    llm_router = LLMRouter(custom_task_routes=company_profile.task_routes)

    if NotificationDispatcher:
        notifier = NotificationDispatcher()

    # Scheduler
    if PipelineScheduler:
        pipeline_scheduler = PipelineScheduler(settings.scheduler_timezone)
        pipeline_scheduler.configure(
            pipeline_func=run_full_pipeline,
            scrape_hour=settings.scrape_hour,
        )
        pipeline_scheduler.start()

    logger.success("Platform started successfully")
    yield

    # Shutdown
    if pipeline_scheduler:
        pipeline_scheduler.stop()
    logger.info("Platform shut down")


# ── App ───────────────────────────────────────────────────
app = FastAPI(
    title="Marketing Department Automation",
    description="AI-powered marketing automation platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated assets
if os.path.exists("./data/outputs"):
    app.mount("/outputs", StaticFiles(directory="./data/outputs"), name="outputs")

# Register template API router
from api.templates import router as templates_router
app.include_router(templates_router, prefix="/api")


# ── Pydantic Models ──────────────────────────────────────

class PipelineRunRequest(BaseModel):
    campaign_topic: Optional[str] = None   # e.g. "Mother's Day", "Black Friday"
    location: Optional[str] = None         # e.g. "New York", "Global"
    custom_prompt: Optional[str] = None    # User directives for agents & scrapers
    video_duration_seconds: int = 15       # 5 to 30
    video_template_id: Optional[str] = None
    presentation_template_id: Optional[str] = None
    graphic_size: str = "both"

class PipelineResponse(BaseModel):
    run_id: str
    status: str
    message: str

class CampaignAction(BaseModel):
    action: str  # "approve" or "reject"

class SearchQuery(BaseModel):
    query: str
    n_results: int = 10

def push_to_stream(run_id: str, message: str):
    """Push a text message to the SSE queue for the given run_id."""
    if run_id in PIPELINE_PROGRESS:
        PIPELINE_PROGRESS[run_id]["live_logs"].append(message)
    if run_id in STREAM_QUEUES:
        # Convert dict to JSON string for SSE format
        stream_msg = json.dumps({"type": "log", "text": message})
        try:
            STREAM_QUEUES[run_id].put_nowait(stream_msg)
        except asyncio.QueueFull:
            pass

def push_progress(run_id: str, step: int, message: str, total_steps: int = 5):
    """Push a progress update to the SSE queue."""
    if run_id in PIPELINE_PROGRESS:
        PIPELINE_PROGRESS[run_id].update({"step": step, "message": message, "total_steps": total_steps})
    if run_id in STREAM_QUEUES:
        stream_msg = json.dumps({"type": "progress", "step": step, "message": message, "total_steps": total_steps})
        try:
            STREAM_QUEUES[run_id].put_nowait(stream_msg)
        except asyncio.QueueFull:
            pass

# ── Full Pipeline ────────────────────────────────────────

async def run_full_pipeline(run_id: Optional[str] = None, campaign_topic: Optional[str] = None, location: Optional[str] = None, custom_prompt: Optional[str] = None, video_duration_seconds: int = 15, video_template_id: Optional[str] = None, presentation_template_id: Optional[str] = None, graphic_size: str = "both"):
    """Execute the complete marketing automation pipeline."""
    run_id = run_id or str(uuid.uuid4())[:8]
    topic_label = campaign_topic or "General"
    location_label = location or "Global"
    logger.info(f"[Pipeline:{run_id}] Starting full pipeline | Topic: {topic_label} | Location: {location_label} | Duration: {video_duration_seconds}s")
    
    PIPELINE_PROGRESS[run_id] = {
        "step": 0, "total_steps": 5, "message": "Starting pipeline...", "status": "running", "live_logs": []
    }

    session = await get_session_direct()
    
    try:
        # Track pipeline run
        pipeline_run = PipelineRun(
            run_id=run_id,
            status="running",
            started_at=datetime.utcnow(),
        )
        session.add(pipeline_run)
        await session.commit()

        # ── Load company profile for this run ─────────
        profile = company_profile or CompanyProfile()
        platforms = profile.enabled_platforms
        logger.info(f"[Pipeline:{run_id}] Company: {profile.company_name} | Industry: {profile.industry}")

        # ── Step 1: Scraping ──────────────────────────
        logger.info(f"[Pipeline:{run_id}] Step 1/5: Scraping")
        scrape_msg = "Scraping campaigns related to '{campaign_topic}'..." if campaign_topic else "Scraping fresh content from platforms..."
        push_progress(run_id, 1, scrape_msg)
        push_to_stream(run_id, "🚀 Initializing marketing research engine...")
        
        all_items = []
        
        # ── Check for Cached Content (7-Day Skip) ─────
        from sqlalchemy import and_
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        
        if campaign_topic:
            try:
                # Find content with matching keywords in title or text from the last week
                topic_query = f"%{campaign_topic}%"
                cached_res = await session.execute(
                    select(ScrapedContent).where(
                        and_(
                            ScrapedContent.scraped_at >= one_week_ago,
                            (ScrapedContent.title.ilike(topic_query) | ScrapedContent.text.ilike(topic_query))
                        )
                    ).limit(50)
                )
                cached_items = cached_res.scalars().all()
                
                if len(cached_items) >= 15:
                    logger.info(f"[Pipeline:{run_id}] Found {len(cached_items)} cached items for '{campaign_topic}' from the last 7 days. Skipping fresh scrape.")
                    push_to_stream(run_id, f"♻️ Found {len(cached_items)} fresh items in local cache. Utilizing existing research data to optimize speed...")
                    all_items = cached_items
                    # Jump directly to Analysis
                else:
                    logger.info(f"[Pipeline:{run_id}] Insufficient cached content ({len(cached_items)}). Proceeding with fresh scrape.")
            except Exception as e:
                logger.warning(f"[Pipeline:{run_id}] Cache check failed: {e}")

        if not all_items:
            # Proceed with standard scraping if no cache found or topic is missing
            push_to_stream(run_id, "🔍 No fresh local research found. Launching global scraper network...")

        # Build dynamic search queries from campaign_topic and custom_prompt
        base_yt_queries = list(profile.youtube_queries)
        base_hashtags = list(profile.hashtags)
        base_gt_keywords = list(profile.topics[:5])
        google_trends_geos = ["", "US", "GB", "CA", "AU"] # Default global baseline
        local_keywords_configs = []

        if campaign_topic:
            topic_slug = campaign_topic.lower().replace(" ", "")
            loc_context = f"Region/Location targeting: {location}" if location else "Global audience targeting (worldwide)"
            prompt = f"""
We are running a marketing campaign for: "{campaign_topic}".
Context: {loc_context}

Provide a JSON object containing optimized search strategies for this. If global, provide universally dominant search regions. If a specific region, prioritize that region and surrounding major countries.

Return ONLY raw JSON with these exact keys:
{{
  "tiktok_hashtags": ["list of 6 hashtags, including local language if applicable"],
  "youtube_queries": ["list of 3 search queries, including local language if applicable"],
  "google_trends_geos": ["list of 3-5 ISO codes to track (e.g., US, IN, NP, GB, CA, etc.)"],
  "local_language_keywords": [
     {{"keywords": ["keyword1", "keyword2", "keyword3"], "geo": "ISO_CODE", "label": "Country (Language)"}}
  ]
}}
"""
            try:
                logger.info(f"[Pipeline:{run_id}] Fetching localized global strategy via LLM...")
                import re as re_local
                from agents.router import LLMRouter
                llm_router = LLMRouter()
                res = await llm_router.generate(
                    prompt=prompt.strip(),
                    task_type="scoring",  # Use fast model
                    system_prompt="You are a JSON-only global market localization expert. Output valid JSON only, no markdown.",
                    temperature=0.4
                )
                match = re_local.search(r'\{.*\}', res.get("text", ""), re_local.DOTALL)
                if match:
                    loc_data = json.loads(match.group(0))
                    
                    if loc_data.get("tiktok_hashtags"):
                        base_hashtags = loc_data["tiktok_hashtags"] + base_hashtags[:2]
                    if loc_data.get("youtube_queries"):
                        base_yt_queries = loc_data["youtube_queries"] + base_yt_queries[:2]
                    if loc_data.get("google_trends_geos"):
                        google_trends_geos = loc_data["google_trends_geos"]
                    if loc_data.get("local_language_keywords"):
                        local_keywords_configs = loc_data["local_language_keywords"]
                        
                logger.info(f"[Pipeline:{run_id}] Loc Strategy Applied -> Geos: {google_trends_geos}")
            except Exception as e:
                logger.warning(f"[Pipeline:{run_id}] Failed to get dynamic localization: {e}, using defaults")
                
                # Default fallbacks if LLM fails
                prompt_modifier = custom_prompt[:25] if custom_prompt else ""
                base_yt_queries = [
                    f"{campaign_topic} {prompt_modifier} marketing campaign".strip(),
                    f"{campaign_topic} ad commercial".strip()
                ] + base_yt_queries[:2]
                base_hashtags = [topic_slug, f"{topic_slug}marketing"] + base_hashtags[:2]

            # Ensure Google Trends gets the base keyword
            if not campaign_topic in base_gt_keywords:
                prompt_modifier = custom_prompt[:25] if custom_prompt else profile.industry
                base_gt_keywords = [
                    campaign_topic, 
                    f"{campaign_topic} marketing",
                    prompt_modifier
                ] + base_gt_keywords[:2]

        # ── Run all scrapers with error isolation ──────
        scraper_health = {}

        # YouTube
        if platforms.get("youtube", True) and YouTubeScraper:
            try:
                push_to_stream(run_id, "🔍 Mining YouTube for industry trends & video content...")
                yt_channel_ids = profile.youtube_channel_ids or settings.youtube_channel_ids
                yt_scraper = YouTubeScraper(
                    channel_ids=yt_channel_ids,
                    search_queries=base_yt_queries,
                    delay_seconds=settings.scrape_delay_seconds,
                    max_items=settings.max_items_per_platform,
                )
                yt_items = await yt_scraper.run()
                all_items.extend(yt_items)
                scraper_health["youtube"] = {"items": len(yt_items), "status": "ok"}
                push_to_stream(run_id, f"✅ YouTube mining complete: {len(yt_items)} items found.")
            except Exception as e:
                logger.error(f"[Pipeline:{run_id}] YouTube scraper failed: {e}")
                scraper_health["youtube"] = {"items": 0, "status": f"error: {e}"}
                push_to_stream(run_id, "⚠️ YouTube mining skipped due to an error.")

        # TikTok
        if platforms.get("tiktok", True) and TikTokScraper:
            try:
                push_to_stream(run_id, "📱 Scanning TikTok hashtags for viral patterns...")
                tt_scraper = TikTokScraper(
                    hashtags=base_hashtags,
                    delay_seconds=settings.scrape_delay_seconds + 1,
                    max_items=min(settings.max_items_per_platform, 100),
                )
                tt_items = await tt_scraper.run()
                all_items.extend(tt_items)
                scraper_health["tiktok"] = {"items": len(tt_items), "status": "ok"}
                push_to_stream(run_id, f"✅ TikTok data acquired: {len(tt_items)} videos indexed.")
            except Exception as e:
                logger.error(f"[Pipeline:{run_id}] TikTok scraper failed: {e}")
                scraper_health["tiktok"] = {"items": 0, "status": f"error: {e}"}
                push_to_stream(run_id, "⚠️ TikTok scan failed.")

        # News/RSS
        if platforms.get("news_rss", True) and NewsScraper:
            try:
                push_to_stream(run_id, "📰 Reading industry news & RSS feeds...")
                rss_feeds = profile.rss_feeds or settings.rss_feeds
                news_scraper = NewsScraper(
                    rss_feeds=rss_feeds,
                    delay_seconds=settings.scrape_delay_seconds,
                    max_items=settings.max_items_per_platform,
                )
                news_items = await news_scraper.run()
                all_items.extend(news_items)
                scraper_health["news"] = {"items": len(news_items), "status": "ok"}
                push_to_stream(run_id, f"✅ Industry news ingested: {len(news_items)} articles.")
            except Exception as e:
                logger.error(f"[Pipeline:{run_id}] News scraper failed: {e}")
                scraper_health["news"] = {"items": 0, "status": f"error: {e}"}
                push_to_stream(run_id, "⚠️ News/RSS ingest failed.")

        # Google Trends
        if platforms.get("google_trends", True) and GoogleTrendsScraper:
            try:
                push_to_stream(run_id, "📈 Analyzing Google Trends for search volume & keyword velocity...")
                gt_kwargs = {
                    "industry_keywords": base_gt_keywords,
                    "delay_seconds": settings.scrape_delay_seconds + 1,
                    "max_items": min(settings.max_items_per_platform, 40),
                    "geos": google_trends_geos,
                }
                gt_scraper = GoogleTrendsScraper(**gt_kwargs)
                gt_scraper.local_configs = local_keywords_configs
                gt_items = await gt_scraper.run()
                all_items.extend(gt_items)
                scraper_health["google_trends"] = {"items": len(gt_items), "status": "ok"}
                push_to_stream(run_id, f"✅ Market demand signals ingested: {len(gt_items)} trends.")
            except Exception as e:
                logger.error(f"[Pipeline:{run_id}] Google Trends scraper failed: {e}")
                scraper_health["google_trends"] = {"items": 0, "status": f"error: {e}"}
                push_to_stream(run_id, "⚠️ Google Trends analysis failed.")

        # Reddit
        if platforms.get("reddit", True) and RedditScraper:
            try:
                push_to_stream(run_id, "📡 Tapping into Reddit discussions & community feedback...")
                reddit_queries = list(base_yt_queries[:3]) if campaign_topic else []
                reddit_scraper = RedditScraper(
                    search_queries=reddit_queries,
                    delay_seconds=settings.scrape_delay_seconds,
                    max_items=min(settings.max_items_per_platform, 80),
                )
                reddit_items = await reddit_scraper.run()
                all_items.extend(reddit_items)
                scraper_health["reddit"] = {"items": len(reddit_items), "status": "ok"}
                push_to_stream(run_id, f"✅ Reddit intelligence gathered: {len(reddit_items)} threads.")
            except Exception as e:
                logger.error(f"[Pipeline:{run_id}] Reddit scraper failed: {e}")
                scraper_health["reddit"] = {"items": 0, "status": f"error: {e}"}
                push_to_stream(run_id, "⚠️ Reddit scan skipped.")

        # Twitter/X
        if platforms.get("twitter", True) and TwitterScraper:
            try:
                push_to_stream(run_id, "🐦 Monitoring X/Twitter for real-time viral trends...")
                twitter_queries = base_yt_queries[:3] if campaign_topic else [
                    "digital marketing tips", "marketing automation", "social media strategy",
                ]
                twitter_scraper = TwitterScraper(
                    search_queries=twitter_queries,
                    delay_seconds=settings.scrape_delay_seconds + 1,
                    max_items=min(settings.max_items_per_platform, 60),
                )
                twitter_items = await twitter_scraper.run()
                all_items.extend(twitter_items)
                scraper_health["twitter"] = {"items": len(twitter_items), "status": "ok"}
                push_to_stream(run_id, f"✅ X/Twitter pulse mining complete: {len(twitter_items)} posts.")
            except Exception as e:
                logger.error(f"[Pipeline:{run_id}] Twitter scraper failed: {e}")
                scraper_health["twitter"] = {"items": 0, "status": f"error: {e}"}
                push_to_stream(run_id, "⚠️ X/Twitter monitoring failed.")

        # Competitor Websites
        if platforms.get("competitor", True) and CompetitorScraper and profile.competitors:
            try:
                push_to_stream(run_id, "🕵️ Analyzing competitor websites for strategic updates...")
                comp_scraper = CompetitorScraper(
                    competitors=profile.competitors,
                    delay_seconds=settings.scrape_delay_seconds + 1,
                    max_items=min(settings.max_items_per_platform, 40),
                )
                comp_items = await comp_scraper.run()
                all_items.extend(comp_items)
                scraper_health["competitor"] = {"items": len(comp_items), "status": "ok"}
                push_to_stream(run_id, f"✅ Competitor intelligence unlocked: {len(comp_items)} insights.")
            except Exception as e:
                logger.error(f"[Pipeline:{run_id}] Competitor scraper failed: {e}")
                scraper_health["competitor"] = {"items": 0, "status": f"error: {e}"}
                push_to_stream(run_id, "⚠️ Competitor website analysis failed.")

        # Meme & Viral Content
        if platforms.get("memes", True) and MemeScraper:
            try:
                push_to_stream(run_id, "🤡 Harvesting viral memes & internet culture...")
                meme_scraper = MemeScraper(
                    delay_seconds=settings.scrape_delay_seconds + 1,
                    max_items=min(settings.max_items_per_platform, 60),
                )
                meme_items = await meme_scraper.run()
                all_items.extend(meme_items)
                scraper_health["memes"] = {"items": len(meme_items), "status": "ok"}
                push_to_stream(run_id, f"✅ Meme harvesting complete: {len(meme_items)} items.")
            except Exception as e:
                logger.error(f"[Pipeline:{run_id}] Meme scraper failed: {e}")
                scraper_health["memes"] = {"items": 0, "status": f"error: {e}"}
                push_to_stream(run_id, "⚠️ Meme harvesting failed.")

        logger.info(f"[Pipeline:{run_id}] Scraped {len(all_items)} total items | Health: {json.dumps(scraper_health)}")
        PIPELINE_PROGRESS[run_id]["scraper_health"] = scraper_health

        # Save to database
        for item in all_items:
            existing = await session.execute(
                select(ScrapedContent).where(ScrapedContent.content_id == item.content_id)
            )
            if existing.scalar_one_or_none():
                continue

            db_item = ScrapedContent(
                platform=item.platform,
                content_id=item.content_id,
                title=item.title,
                text=item.text,
                url=item.url,
                author=item.author,
                metadata_json=json.dumps(item.metadata),
                view_count=item.view_count,
                like_count=item.like_count,
                comment_count=item.comment_count,
                published_at=item.published_at,
            )
            session.add(db_item)

        await session.commit()

        # Add to vector store
        if embedding_store and all_items:
            embedding_store.add_content_batch(
                doc_ids=[item.content_id for item in all_items],
                texts=[item.text[:500] for item in all_items],
                metadatas=[{"platform": item.platform, "title": item.title} for item in all_items],
            )

        pipeline_run.items_scraped = len(all_items)

        # ── Step 2: Analysis ──────────────────────────
        logger.info(f"[Pipeline:{run_id}] Step 2/5: Analysis")
        push_progress(run_id, 2, "Analyzing sentiment and extracting topics...")
        analysis_pipeline = AnalysisPipeline()
        items_for_analysis = [item.to_dict() for item in all_items]
        analysis_brief = await analysis_pipeline.run(items_for_analysis)

        # Save analysis results
        for item_analysis in analysis_brief.get("item_analyses", []):
            content_result = await session.execute(
                select(ScrapedContent).where(
                    ScrapedContent.content_id == item_analysis.get("content_id")
                )
            )
            content = content_result.scalar_one_or_none()
            if content:
                ar = AnalysisResult(
                    content_id=content.id,
                    sentiment_label=item_analysis.get("sentiment", {}).get("label"),
                    sentiment_score=item_analysis.get("sentiment", {}).get("score"),
                    emotion_label=item_analysis.get("emotion", {}).get("label"),
                    emotion_scores=json.dumps(item_analysis.get("emotion", {}).get("all_scores", {})),
                    topic_id=item_analysis.get("topic_id"),
                )
                session.add(ar)

        await session.commit()
        pipeline_run.items_analyzed = len(analysis_brief.get("item_analyses", []))

        # ── Step 3: Agent Council ─────────────────────
        logger.info(f"[Pipeline:{run_id}] Step 3/5: Agent Council")
        push_progress(run_id, 3, "Agent Council is debating strategy & copy...")
        
        def council_progress(agent_name, msg):
            log_entry = {
                "agent": agent_name,
                "message": msg,
            }
            if "live_logs" not in PIPELINE_PROGRESS[run_id]:
                PIPELINE_PROGRESS[run_id]["live_logs"] = []
            PIPELINE_PROGRESS[run_id]["live_logs"].append(log_entry)
            push_to_stream(run_id, f"[{agent_name}] {msg}")
            
        agent_context = profile.get_agent_context()
        if campaign_topic:
            agent_context += f"\n\nCAMPAIGN FOCUS: This campaign is specifically about '{campaign_topic}'.\nLocation target: {location or 'Global'}.\nAll content MUST be tailored around this theme."
        
        if custom_prompt:
            agent_context += f"\n\nCRITICAL USER DIRECTIVE: {custom_prompt}\n(You MUST incorporate this directive heavily into the strategy and copy)."

        if video_duration_seconds:
            scene_count = max(1, video_duration_seconds // 5)
            agent_context += f"\n\nVIDEO REQUIREMENTS: The final output must be exactly {video_duration_seconds} seconds long. You MUST structure the video script into exactly {scene_count} scenes (assuming ~5 seconds per scene)."

        council = AgentCouncil(router=llm_router, company_context=agent_context)
        council_output = await council.run(
            analysis_brief, 
            progress_callback=council_progress,
            video_template_id=video_template_id,
            presentation_template_id=presentation_template_id
        )

        # Save agent logs
        for log in council_output.get("logs", []):
            agent_log = AgentLog(
                run_id=run_id,
                agent_role=log["agent"],
                llm_provider=log["provider"],
                tokens_used=log["tokens"],
                duration_seconds=log["duration"],
            )
            session.add(agent_log)

        await session.commit()

        # ── Step 4: Creative Output ───────────────────
        logger.info(f"[Pipeline:{run_id}] Step 4/5: Creative Output")
        push_progress(run_id, 4, "Generating marketing visual assets...")

        generated_assets = []

        # Generate campaign brief
        brief_gen = BriefGenerator(output_dir=settings.output_dir)
        brief_result = brief_gen.save_brief(council_output, analysis_brief)
        if brief_result.get("pdf_path"):
            generated_assets.append(brief_result["pdf_path"])

        # Generate Remotion Video
        if VideoGenerator:
            try:
                vid_gen = VideoGenerator(profile_data={"company": profile.dict()}, run_id=run_id)
                video_res = await vid_gen.generate_async({
                    "video_scenes": council_output.get("video_scenes", []),
                    "brand_config": council_output.get("video_brand_config", {}),
                    "template_id": video_template_id,
                    "video_duration_seconds": video_duration_seconds
                })
                if video_res and "video_path" in video_res:
                    generated_assets.append(video_res["video_path"])
            except Exception as e:
                logger.error(f"Video generation failed: {e}")

        # Generate Display Graphics (Enhanced with 50+ templates + LAYERED output)
        try:
            from creative.image_gen_enhanced import ImageGenerator
            img_gen = ImageGenerator(profile_data={"company": profile.dict()}, run_id=run_id)
            img_res = await img_gen.generate_async({
                "graphics_config": council_output.get("graphics_config", {}),
                "graphic_size": graphic_size,
                "num_variations": 15,  # Generate 15 professional design variations
                "output_format": "layered"  # Output layered PNGs like Canva MCP
            })
            if img_res and "image_urls" in img_res:
                generated_assets.extend(img_res["image_urls"])
                logger.success(f"[Pipeline:{run_id}] Generated {len(img_res['image_urls'])} layered marketing designs!")
                logger.info(f"[Pipeline:{run_id}] Each design includes 5 editable layers (background, products, gradient, text, logo)")
        except Exception as e:
            logger.error(f"Static Graphic generation failed: {e}")
            import traceback
            traceback.print_exc()

        # Save campaign to database
        agents = council_output.get("agents", {})
        # Collect debates with verdicts
        debates = {}
        for agent_name, agent_data in agents.items():
            if "debate" in agent_data:
                verdict = agent_data.get("verdict", "")
                raw_debate = agent_data["debate"]
                # Combine verdict + raw debate so frontend can parse them
                if verdict:
                    debates[agent_name] = f"{verdict}\n---\n{raw_debate}"
                else:
                    debates[agent_name] = raw_debate

        campaign = Campaign(
            title=f"Campaign — {date.today().strftime('%B %d, %Y')}",
            status="pending",
            summary=agents.get("strategy_planner", {}).get("output", "")[:500],
            target_audience="See strategy section",
            social_copy=json.dumps({"raw": agents.get("copywriter", {}).get("output", "")}),
            visual_direction=agents.get("creative_director", {}).get("output", ""),
            trend_data=json.dumps({"raw": agents.get("trend_analyst", {}).get("output", "")}),
            strategy=agents.get("strategy_planner", {}).get("output", ""),
            quality_score=council_output.get("quality_score", 0),
            critic_feedback=agents.get("critic", {}).get("output", ""),
            raw_scraped_data=json.dumps(items_for_analysis, default=str),
            debate_logs=json.dumps(debates),
            video_script=json.dumps({
                "template_id": video_template_id or "mesh_abstract_1",
                "scenes": council_output.get("video_scenes", []),
                "brand_config": council_output.get("video_brand_config", {})
            }),
            slides_json=json.dumps({
                "template_id": presentation_template_id or "clay_minimal_1",
                "slides": council_output.get("slides", [])
            }),
            run_id=run_id,
            brief_markdown=brief_result.get("markdown_content", ""),
            brief_pdf_path=brief_result.get("pdf_path"),
        )
        session.add(campaign)
        await session.commit()

        # Create CreativeAsset entries even before linking them to the campaign ID
        for asset_path in generated_assets:
            asset_type = "document"
            if asset_path.endswith(".mp4"):
                asset_type = "video"
            elif asset_path.endswith(".png") or asset_path.endswith(".jpg"):
                asset_type = "image"
            
            new_asset = CreativeAsset(
                campaign_id=campaign.id,
                asset_type=asset_type,
                file_path=asset_path,
                prompt=campaign.title,
            )
            session.add(new_asset)
        
        await session.commit()

        pipeline_run.campaigns_generated = 1
        pipeline_run.assets_created = len(generated_assets)

        # ── Step 5: Notifications ─────────────────────
        logger.info(f"[Pipeline:{run_id}] Step 5/5: Notifications")
        push_progress(run_id, 5, "Finalizing outputs and notifying team...")
        if notifier:
            await notifier.send_campaign_summary(council_output)

        # Mark pipeline complete
        pipeline_run.status = "completed"
        pipeline_run.completed_at = datetime.utcnow()
        await session.commit()

        PIPELINE_PROGRESS[run_id].update({"status": "completed", "message": "Pipeline completed successfully!"})
        logger.success(f"[Pipeline:{run_id}] Complete!")
        return council_output

    except Exception as e:
        logger.error(f"[Pipeline:{run_id}] Failed: {e}")
        pipeline_run.status = "failed"
        pipeline_run.errors = str(e)
        PIPELINE_PROGRESS[run_id] = {"status": "failed", "message": f"Error: {str(e)}", "step": 0, "total_steps": 5}
        await session.commit()
        raise
    finally:
        push_to_stream(run_id, "EOF")
        await session.close()


# ── API Routes ────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/pipeline/run", response_model=PipelineResponse)
async def trigger_pipeline(background_tasks: BackgroundTasks, body: PipelineRunRequest = PipelineRunRequest()):
    """Manually trigger a full pipeline run with optional campaign context."""
    run_id = str(uuid.uuid4())[:8]
    background_tasks.add_task(
        run_full_pipeline, 
        run_id, 
        body.campaign_topic, 
        body.location, 
        body.custom_prompt,
        body.video_duration_seconds,
        body.video_template_id,
        body.presentation_template_id,
        body.graphic_size
    )
    msg = "Pipeline started in background"
    if body.campaign_topic:
        msg = f"Pipeline started for '{body.campaign_topic}' campaign"
    return PipelineResponse(
        run_id=run_id,
        status="started",
        message=msg,
    )


@app.get("/api/pipeline/status/{run_id}")
async def get_pipeline_status(run_id: str):
    """Get the live progress of a pipeline execution."""
    if run_id in PIPELINE_PROGRESS:
        return PIPELINE_PROGRESS[run_id]
    return {"status": "unknown", "message": "Pipeline run not found or not tracked."}


@app.post("/api/upload")
async def upload_asset(file: UploadFile = File(...)):
    """Uploads an image or asset and returns its local URL"""
    try:
        # Save to the outputs/assets directory mapped to /outputs via StaticFiles
        import shutil
        upload_dir = os.path.join(settings.output_dir, "assets")
        os.makedirs(upload_dir, exist_ok=True)
        
        # generate random name
        ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
        filename = f"asset_{str(uuid.uuid4())[:8]}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Returning url that corresponds to our StaticFiles mount
        return {"url": f"/outputs/assets/{filename}", "filename": filename}
    except Exception as e:
        logger.error(f"Failed to upload asset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get dashboard summary data."""
    session = await get_session_direct()
    try:
        # Total content
        total_content = await session.execute(
            select(func.count(ScrapedContent.id))
        )
        content_count = total_content.scalar() or 0

        # Platform breakdown
        platform_counts = await session.execute(
            select(ScrapedContent.platform, func.count(ScrapedContent.id))
            .group_by(ScrapedContent.platform)
        )
        platforms = {row[0]: row[1] for row in platform_counts.all()}

        # Today's content
        today = date.today().isoformat()
        today_content = await session.execute(
            select(func.count(ScrapedContent.id))
            .where(func.date(ScrapedContent.scraped_at) == today)
        )
        today_count = today_content.scalar() or 0

        # Campaigns
        total_campaigns = await session.execute(
            select(func.count(Campaign.id))
        )
        campaign_count = total_campaigns.scalar() or 0

        pending_campaigns = await session.execute(
            select(func.count(Campaign.id))
            .where(Campaign.status == "pending")
        )
        pending_count = pending_campaigns.scalar() or 0

        # Latest sentiment
        latest_sentiments = await session.execute(
            select(AnalysisResult.sentiment_label, func.count(AnalysisResult.id))
            .group_by(AnalysisResult.sentiment_label)
        )
        sentiment_dist = {row[0]: row[1] for row in latest_sentiments.all() if row[0]}

        # Recent pipeline runs
        recent_runs = await session.execute(
            select(PipelineRun)
            .order_by(desc(PipelineRun.started_at))
            .limit(5)
        )
        runs = []
        for run in recent_runs.scalars().all():
            runs.append({
                "run_id": run.run_id,
                "status": run.status,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "items_scraped": run.items_scraped,
                "campaigns_generated": run.campaigns_generated,
            })

        # LLM usage
        llm_usage = llm_router.get_usage_stats() if llm_router else {}

        return {
            "total_content": content_count,
            "today_content": today_count,
            "platforms": platforms,
            "total_campaigns": campaign_count,
            "pending_campaigns": pending_count,
            "sentiment_distribution": sentiment_dist,
            "recent_runs": runs,
            "llm_usage": llm_usage,
            "vector_store": embedding_store.get_stats() if embedding_store else {},
        }
    finally:
        await session.close()


@app.get("/api/campaigns")
async def list_campaigns(
    status: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    """List campaign briefs."""
    session = await get_session_direct()
    try:
        query = select(Campaign).order_by(desc(Campaign.created_at))
        if status:
            query = query.where(Campaign.status == status)
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        campaigns = []
        for c in result.scalars().all():
            campaigns.append({
                "id": c.id,
                "title": c.title,
                "status": c.status,
                "summary": c.summary[:200] if c.summary else "",
                "quality_score": c.quality_score,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "has_pdf": bool(c.brief_pdf_path),
            })
        return {"campaigns": campaigns, "total": len(campaigns)}
    finally:
        await session.close()


@app.get("/api/campaigns/{campaign_id}")
async def get_campaign(campaign_id: int):
    """Get full campaign detail."""
    session = await get_session_direct()
    try:
        result = await session.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        c = result.scalar_one_or_none()
        if not c:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Get assets
        assets_result = await session.execute(
            select(CreativeAsset).where(CreativeAsset.campaign_id == campaign_id)
        )
        assets = []
        for a in assets_result.scalars().all():
            assets.append({
                "id": a.id,
                "type": a.asset_type,
                "file_path": a.file_path,
                "prompt": a.prompt,
            })

        return {
            "id": c.id,
            "title": c.title,
            "status": c.status,
            "summary": c.summary,
            "strategy": c.strategy,
            "social_copy": c.social_copy,
            "visual_direction": c.visual_direction,
            "quality_score": c.quality_score,
            "critic_feedback": c.critic_feedback,
            "raw_scraped_data": c.raw_scraped_data,
            "debate_logs": c.debate_logs,
            "video_script": c.video_script,
            "brief_markdown": c.brief_markdown,
            "brief_pdf_path": c.brief_pdf_path,
            "slides_json": c.slides_json,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "assets": assets,
        }
    finally:
        await session.close()


async def generate_campaign_video_async(campaign_id: int):
    """Background task to generate video locally via remotion after campaign approval."""
    try:
        session = await get_session_direct()
        result = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = result.scalar_one_or_none()
        if not campaign or not campaign.video_script:
            await session.close()
            return
            
        video_data = json.loads(campaign.video_script)
        if not video_data:
            await session.close()
            return
            
        video_scenes = video_data.get("scenes", []) if isinstance(video_data, dict) else video_data
        brand_config = video_data.get("brand_config", {}) if isinstance(video_data, dict) else {}

        if not video_scenes:
            await session.close()
            return
            
        if VideoGenerator is not None:
            vid_gen = VideoGenerator(profile_data=company_profile.data, run_id=f"camp_{campaign_id}")
            # Merge brand_config into the brief passed to generate_async
            video_result = await vid_gen.generate_async({
                "video_scenes": video_scenes,
                "brand_config": brand_config
            })
            
            if "stream_url" in video_result:
                asset = CreativeAsset(
                    campaign_id=campaign_id,
                    asset_type="video",
                    file_path=video_result["stream_url"],
                    prompt=video_result.get("description", "Viral Motion Graphics")
                )
                session.add(asset)
                campaign.status = "approved"
                await session.commit()
                
                if notifier:
                    await notifier.send_all(
                        subject="Video Generation Complete",
                        message=f"Video for campaign '{campaign.title}' successfully generated.",
                    )
            else:
                campaign.status = "pending"
                await session.commit()
                logger.error(f"Video generation returned no stream_url: {video_result}")
        
        await session.close()
    except Exception as e:
        logger.error(f"Background video generation failed: {e}")
        try:
            session2 = await get_session_direct()
            res2 = await session2.execute(select(Campaign).where(Campaign.id == campaign_id))
            c2 = res2.scalar_one_or_none()
            if c2:
                c2.status = "pending"
                await session2.commit()
            await session2.close()
        except:
            pass



@app.get("/api/campaigns/{campaign_id}/video-progress")
async def get_video_progress(campaign_id: int):
    """Get real-time video generation progress for a campaign."""
    from creative.video_gen import VIDEO_PROGRESS
    run_key = f"camp_{campaign_id}"
    if run_key in VIDEO_PROGRESS:
        return VIDEO_PROGRESS[run_key]
    
    # Check campaign status as fallback
    session = await get_session_direct()
    try:
        result = await session.execute(select(Campaign.status).where(Campaign.id == campaign_id))
        row = result.first()
        if row and row[0] == "approved":
            return {"step": 1, "total_steps": 1, "message": "Video ready!", "percent": 100}
        elif row and row[0] == "generating_video":
            return {"step": 0, "total_steps": 1, "message": "Starting...", "percent": 0}
        return {"step": 0, "total_steps": 1, "message": "Not started", "percent": 0}
    finally:
        await session.close()


@app.post("/api/campaigns/{campaign_id}/action")
async def campaign_action(campaign_id: int, action: CampaignAction, background_tasks: BackgroundTasks):
    """Approve or reject a campaign."""
    session = await get_session_direct()
    try:
        result = await session.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        if action.action == "approve":
            campaign.status = "generating_video"
            background_tasks.add_task(generate_campaign_video_async, campaign_id)
        elif action.action == "reject":
            campaign.status = "rejected"
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        await session.commit()

        # Notify about the action
        if notifier:
            await notifier.send_all(
                subject=f"Campaign {action.action.upper()}",
                message=f"Campaign '{campaign.title}' has been {action.action}d.",
            )

        return {"status": campaign.status, "campaign_id": campaign_id}
    finally:
        await session.close()


@app.get("/api/gallery")
async def get_gallery(limit: int = Query(50, le=200)):
    """Get creative assets gallery, including pending/draft videos with full campaign context."""
    session = await get_session_direct()
    try:
        # 1. Get actual assets
        asset_res = await session.execute(
            select(CreativeAsset)
            .order_by(desc(CreativeAsset.created_at))
            .limit(limit)
        )
        assets = []
        existing_campaign_video_ids = set()
        for a in asset_res.scalars().all():
            assets.append({
                "id": a.id,
                "campaign_id": a.campaign_id,
                "type": a.asset_type,
                "file_path": a.file_path,
                "prompt": a.prompt,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            })
            if a.asset_type == 'video' and a.campaign_id:
                existing_campaign_video_ids.add(a.campaign_id)
        
        # 2. Get Campaigns with video_script but NO video asset yet
        draft_res = await session.execute(
            select(Campaign)
            .where(Campaign.video_script != None)
            .where(Campaign.video_script != "[]")
            .where(Campaign.status.in_(["pending", "generating_video"]))
            .order_by(desc(Campaign.created_at))
            .limit(limit)
        )
        
        for c in draft_res.scalars().all():
            if c.id not in existing_campaign_video_ids:
                try:
                    script_data = json.loads(c.video_script)
                    if isinstance(script_data, dict):
                        script = script_data.get("scenes", script_data.get("video_scenes", []))
                    else:
                        script = script_data
                    if not isinstance(script, list):
                        script = []
                except:
                    script = []
                
                # Build rich scene previews from the campaign
                scenes = []
                for s in script:
                    if isinstance(s, dict):
                        scenes.append({
                            "text": s.get("text", ""),
                            "voiceover": s.get("voiceover_prompt", ""),
                            "duration_sec": round(s.get("durationInFrames", 90) / 30, 1),
                        })
                
                assets.append({
                    "id": f"draft_{c.id}",
                    "campaign_id": c.id,
                    "type": "draft_video",
                    "status": c.status,
                    "campaign_title": c.title,
                    "campaign_summary": (c.summary or "")[:200],
                    "scenes": scenes,
                    "preview_text": scenes[0]["text"] if scenes else "Draft Video",
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                })

        assets.sort(key=lambda x: x["created_at"] or "", reverse=True)
        return {"assets": assets[:limit]}
    finally:
        await session.close()


@app.get("/api/trends")

async def get_trends():
    """Get trend analysis data."""
    session = await get_session_direct()
    try:
        # Get sentiment distribution over time
        sentiments = await session.execute(
            select(
                func.date(AnalysisResult.analyzed_at).label("date"),
                AnalysisResult.sentiment_label,
                func.count(AnalysisResult.id),
            )
            .group_by(func.date(AnalysisResult.analyzed_at), AnalysisResult.sentiment_label)
            .order_by(func.date(AnalysisResult.analyzed_at))
        )
        sentiment_timeline = {}
        for row in sentiments.all():
            dt = str(row[0])
            if dt not in sentiment_timeline:
                sentiment_timeline[dt] = {}
            sentiment_timeline[dt][row[1] or "unknown"] = row[2]

        # Get top topics
        topics = await session.execute(
            select(AnalysisResult.topic_label, func.count(AnalysisResult.id))
            .where(AnalysisResult.topic_label.isnot(None))
            .group_by(AnalysisResult.topic_label)
            .order_by(desc(func.count(AnalysisResult.id)))
            .limit(20)
        )
        top_topics = [{"name": row[0], "count": row[1]} for row in topics.all()]

        # Emotion distribution
        emotions = await session.execute(
            select(AnalysisResult.emotion_label, func.count(AnalysisResult.id))
            .where(AnalysisResult.emotion_label.isnot(None))
            .group_by(AnalysisResult.emotion_label)
            .order_by(desc(func.count(AnalysisResult.id)))
        )
        emotion_dist = {row[0]: row[1] for row in emotions.all()}

        # Platform content volume
        platform_volume = await session.execute(
            select(
                ScrapedContent.platform,
                func.date(ScrapedContent.scraped_at).label("date"),
                func.count(ScrapedContent.id),
            )
            .group_by(ScrapedContent.platform, func.date(ScrapedContent.scraped_at))
            .order_by(func.date(ScrapedContent.scraped_at))
        )
        volume_timeline = {}
        for row in platform_volume.all():
            dt = str(row[1])
            if dt not in volume_timeline:
                volume_timeline[dt] = {}
            volume_timeline[dt][row[0]] = row[2]

        return {
            "sentiment_timeline": sentiment_timeline,
            "top_topics": top_topics,
            "emotion_distribution": emotion_dist,
            "volume_timeline": volume_timeline,
        }
    finally:
        await session.close()


@app.get("/api/world-pulse")
async def get_world_pulse():
    """Get raw global trends and viral memes from recent scrapes."""
    session = await get_session_direct()
    try:
        import json
        # Fetch latest google trends (limit to recent 200 for broad coverage)
        gt_result = await session.execute(
            select(ScrapedContent)
            .where(ScrapedContent.platform == "google_trends")
            .order_by(desc(ScrapedContent.scraped_at))
            .limit(200)
        )
        gt_items = gt_result.scalars().all()

        # Fetch latest memes (limit 100)
        meme_result = await session.execute(
            select(ScrapedContent)
            .where(ScrapedContent.platform == "memes")
            .order_by(desc(ScrapedContent.scraped_at))
            .limit(100)
        )
        meme_items = meme_result.scalars().all()

        def parse_metadata(item):
            try:
                meta = json.loads(item.metadata_json) if item.metadata_json else {}
            except:
                meta = {}
            return {
                "id": item.id,
                "title": item.title,
                "text": item.text,
                "url": item.url,
                "author": item.author,
                "like_count": item.like_count,
                "comment_count": item.comment_count,
                "scraped_at": item.scraped_at.isoformat() if item.scraped_at else None,
                "metadata": meta
            }

        return {
            "google_trends": [parse_metadata(i) for i in gt_items],
            "memes": [parse_metadata(i) for i in meme_items]
        }
    except Exception as e:
        logger.error(f"World pulse fetch failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch world pulse data")
    finally:
        await session.close()


@app.get("/api/logs")
async def get_logs(limit: int = Query(50, le=200)):
    """Get agent execution logs."""
    session = await get_session_direct()
    try:
        result = await session.execute(
            select(AgentLog)
            .order_by(desc(AgentLog.created_at))
            .limit(limit)
        )
        logs = []
        for log in result.scalars().all():
            logs.append({
                "id": log.id,
                "run_id": log.run_id,
                "agent": log.agent_role,
                "provider": log.llm_provider,
                "tokens": log.tokens_used,
                "duration": log.duration_seconds,
                "quality_score": log.quality_score,
                "error": log.error,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            })
        return {"logs": logs}
    finally:
        await session.close()


@app.delete("/api/pipeline/runs/{run_id}")
async def delete_pipeline_run(run_id: str):
    """Delete an entire pipeline run and all associated data."""
    session = await get_session_direct()
    try:
        from sqlalchemy import delete
        
        # 1. Get campaign IDs to delete assets
        camp_res = await session.execute(select(Campaign.id).where(Campaign.run_id == run_id))
        camp_ids = camp_res.scalars().all()
        
        # 2. Delete assets
        if camp_ids:
            await session.execute(delete(CreativeAsset).where(CreativeAsset.campaign_id.in_(camp_ids)))
        
        # 3. Delete campaigns
        await session.execute(delete(Campaign).where(Campaign.run_id == run_id))
        
        # 4. Delete agent logs
        await session.execute(delete(AgentLog).where(AgentLog.run_id == run_id))
        
        # 5. Delete the run record itself
        await session.execute(delete(PipelineRun).where(PipelineRun.run_id == run_id))
        
        await session.commit()
        return {"status": "success", "message": f"Run {run_id} and all associated data deleted."}
    except Exception as e:
        await session.rollback()
        logger.error(f"Error deleting run {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()


@app.get("/api/llm-usage")
async def get_llm_usage():
    """Get LLM provider usage stats."""
    return llm_router.get_usage_stats() if llm_router else {}


@app.get("/api/scrapers/test")
async def test_scrapers():
    """Test all scrapers and return health status."""
    results = {}

    scrapers_to_test = [
        ("youtube", YouTubeScraper, {"search_queries": ["marketing trends"], "max_items": 3}),
        ("tiktok", TikTokScraper, {"hashtags": ["digitalmarketing"], "max_items": 3}),
        ("news", NewsScraper, {"max_items": 3}),
        ("google_trends", GoogleTrendsScraper, {"max_items": 3}),
        ("reddit", RedditScraper, {"subreddits": ["marketing"], "max_items": 3}),
        ("twitter", TwitterScraper, {"search_queries": ["marketing tips"], "max_items": 3}),
        ("memes", MemeScraper, {"max_items": 3}),
    ]

    for name, cls, kwargs in scrapers_to_test:
        if cls is None:
            results[name] = {"status": "not_installed", "items": 0}
            continue
        try:
            scraper = cls(**kwargs)
            items = await scraper.run()
            results[name] = {
                "status": "ok",
                "items": len(items),
                "sample": items[0].to_dict() if items else None,
            }
        except Exception as e:
            results[name] = {"status": f"error: {str(e)[:200]}", "items": 0}

    return {"scrapers": results}


@app.get("/api/intelligence/brief")
async def get_intelligence_brief():
    """Get raw intelligence summary from latest scraped data without running a full campaign."""
    session = await get_session_direct()
    try:
        from sqlalchemy import desc as sql_desc
        result = await session.execute(
            select(ScrapedContent)
            .order_by(sql_desc(ScrapedContent.scraped_at))
            .limit(100)
        )
        items = []
        platform_counts = {}
        for row in result.scalars().all():
            platform_counts[row.platform] = platform_counts.get(row.platform, 0) + 1
            items.append({
                "platform": row.platform,
                "title": row.title,
                "text": row.text[:300] if row.text else "",
                "url": row.url,
                "scraped_at": row.scraped_at.isoformat() if row.scraped_at else None,
            })

        return {
            "total_items": len(items),
            "platform_breakdown": platform_counts,
            "latest_items": items[:50],
            "generated_at": datetime.utcnow().isoformat(),
        }
    finally:
        await session.close()


@app.post("/api/search")
async def semantic_search(query: SearchQuery):
    """Semantic search over scraped content."""
    if not embedding_store:
        raise HTTPException(status_code=503, detail="Vector store not initialized")

    results = embedding_store.search_content(
        query=query.query,
        n_results=query.n_results,
    )
    return {"results": results, "query": query.query}


@app.get("/api/scheduler/jobs")
async def get_scheduled_jobs():
    """Get scheduled job information."""
    if pipeline_scheduler:
        return {"jobs": pipeline_scheduler.get_jobs()}
    return {"jobs": []}

@app.delete("/api/database/purge")
async def purge_database():
    """Clear all records from the database for a fresh start."""
    session = await get_session_direct()
    try:
        from sqlalchemy import delete
        await session.execute(delete(CreativeAsset))
        await session.execute(delete(AnalysisResult))
        await session.execute(delete(ScrapedContent))
        await session.execute(delete(AgentLog))
        await session.execute(delete(Campaign))
        await session.execute(delete(PipelineRun))
        await session.commit()
        
        # Reset chromadb if initialized
        if embedding_store:
            try:
                import shutil
                shutil.rmtree(settings.chroma_persist_dir, ignore_errors=True)
                # Note: the in-memory instance will still have old data until restart,
                # but ignoring for simplicity unless user restarts server
            except Exception:
                pass
                
        return {"status": "success", "message": "Database completely purged."}
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await session.close()


# ── Company Profile CRUD ──────────────────────────────────

@app.get("/api/profile")
async def get_profile():
    """Get the company profile configuration."""
    if company_profile:
        return company_profile.to_dict()
    return CompanyProfile().to_dict()


@app.put("/api/profile")
async def update_profile(data: dict):
    """Update the company profile configuration."""
    global company_profile
    if not company_profile:
        company_profile = CompanyProfile()
    updated = company_profile.update(data)
    return {"status": "saved", "profile": updated}

@app.get("/api/pipeline/stream/{run_id}")
async def stream_pipeline(run_id: str):
    """Live SSE stream for real-time agent debate."""
    if run_id not in STREAM_QUEUES:
        STREAM_QUEUES[run_id] = asyncio.Queue()
        
    async def event_generator():
        try:
            while True:
                msg = await STREAM_QUEUES[run_id].get()
                if msg == "EOF":
                    yield f"data: {json.dumps({'type': 'end', 'text': 'Pipeline complete'})}\n\n"
                    break
                yield f"data: {msg}\n\n"
        except asyncio.CancelledError:
            pass
            
    from fastapi.responses import StreamingResponse
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Serve Frontend (in production) ────────────────────────
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="frontend-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the React SPA for any non-API routes."""
        file_path = os.path.join(FRONTEND_DIR, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
