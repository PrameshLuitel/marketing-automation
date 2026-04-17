"""
Agent Council — orchestrates 10 specialized marketing agents.
ALL Groq-only. Each agent acts like a senior marketing professional.
Uses 3-way debate with verdict for quality assurance.

Agents:
1. Trend Analyst           — identifies actionable trends from scraped data
2. Market Researcher       — builds audience personas and market sizing
3. Strategy Planner        — creates comprehensive marketing strategy
4. SEO Specialist          — keyword strategy, search optimization
5. Copywriter              — platform-specific copy that converts
6. Creative Director       — visual direction, image prompts
7. Video Director          — video scripts, scenes, pacing
8. Media Buyer             — ad targeting, budget allocation, platform specs
9. Presentation Designer   — executive slide decks
10. Critic                 — multi-model quality assessment
"""

import json
import uuid
import time
import asyncio
from datetime import datetime
from typing import Optional
from loguru import logger

from .router import LLMRouter


class AgentCouncil:
    """
    Orchestrates the 10-agent marketing council.
    Full pipeline: Intelligence → Strategy → Creative → Quality Gate
    """

    def __init__(self, router: Optional[LLMRouter] = None, company_context: str = ""):
        self.router = router or LLMRouter()
        self.company_context = company_context
        self.quality_threshold = 7.0
        self.max_retries = 2

    async def run(
        self,
        analysis_brief: dict,
        progress_callback=None,
        video_template_id=None,
        presentation_template_id=None,
    ) -> dict:
        """
        Run the full 10-agent council pipeline.

        Args:
            analysis_brief: Output from the analysis pipeline
            progress_callback: Optional callback to stream live debate logs
            video_template_id: Target visual shell for video director
            presentation_template_id: Target layout for presentation designer

        Returns:
            Complete campaign output with all agent contributions
        """
        run_id = str(uuid.uuid4())[:8]
        logger.info(f"[Council:{run_id}] Starting 10-agent council")
        start = time.time()

        brief_json = json.dumps(analysis_brief, indent=2, default=str)[:4000]
        ctx = self.company_context
        results = {"run_id": run_id, "agents": {}, "logs": []}

        logger.info(f"========== RAW SCRAPED DATA ==========\n{brief_json[:2000]}...\n======================================")

        # ═════════════════════════════════════════════════════
        # AGENT 1: TREND ANALYST
        # ═════════════════════════════════════════════════════
        trend_output = await self._run_debate_agent(
            agent_name="trend_analyst",
            task_type="trend_analysis",
            system_prompt=TREND_ANALYST_SYSTEM,
            user_prompt=f"""Analyze the following marketing intelligence data and identify the top 5 actionable trends.

{ctx}

For each trend, provide:
1. Trend name and brief description
2. Why it matters for OUR company specifically (reference our industry and audience)
3. Marketing angle we should capitalize on immediately
4. Urgency score (1-10) with justification
5. How our competitors are likely responding
6. Content formats best suited for this trend (video, blog, social, email, etc.)

DATA BRIEF:
{brief_json}""",
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        logger.info(f"\n========== IDENTIFIED TRENDS ==========\n{trend_output[:1000]}...\n=======================================\n")

        # ═════════════════════════════════════════════════════
        # AGENT 2: MARKET RESEARCHER
        # ═════════════════════════════════════════════════════
        researcher_output = await self._run_debate_agent(
            agent_name="market_researcher",
            task_type="market_research",
            system_prompt=MARKET_RESEARCHER_SYSTEM,
            user_prompt=f"""Based on these trends and the raw intelligence data, build a comprehensive market research brief.

{ctx}

TRENDS IDENTIFIED:
{trend_output[:2000]}

ORIGINAL DATA:
{brief_json[:1500]}

Deliver:
1. **Audience Personas** — Define 3 distinct buyer personas with demographics, pain points, motivations, preferred platforms, and content consumption habits
2. **Market Sizing** — Estimate the addressable market for each persona
3. **Customer Journey Map** — For each persona, map: Awareness → Consideration → Decision triggers
4. **Competitive Landscape** — What are competitors doing well? Where are the gaps we can exploit?
5. **Audience Sentiment** — What is the emotional state of our target market right now?
6. **Pain Points** — Top 5 pain points our content should address""",
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        # ═════════════════════════════════════════════════════
        # AGENT 3: STRATEGY PLANNER
        # ═════════════════════════════════════════════════════
        strategy_output = await self._run_debate_agent(
            agent_name="strategy_planner",
            task_type="strategy_planning",
            system_prompt=STRATEGY_PLANNER_SYSTEM,
            user_prompt=f"""Create a comprehensive, actionable marketing strategy based on trends and market research.

{ctx}

TRENDS:
{trend_output[:1500]}

MARKET RESEARCH:
{researcher_output[:1500]}

Include:
1. **Executive Summary** — 3-sentence campaign thesis statement
2. **Strategic Positioning** — How we differentiate from {ctx[:100]}... competitors
3. **Target Audience** — Primary and secondary audiences (from research)
4. **Key Messages** — 5 messaging pillars that resonate with pain points
5. **Channel Strategy** — Which platforms, posting frequency, content mix ratio
6. **Content Pillars** — 3-4 content themes for the next 30 days
7. **Campaign Timeline** — Week-by-week execution plan
8. **KPIs & Metrics** — Specific, measurable goals for each channel
9. **Budget Allocation** — Suggested % split across channels
10. **Risk Mitigation** — Potential pitfalls and backup plans""",
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        # ═════════════════════════════════════════════════════
        # AGENT 4: SEO SPECIALIST
        # ═════════════════════════════════════════════════════
        seo_output = await self._run_debate_agent(
            agent_name="seo_specialist",
            task_type="seo_analysis",
            system_prompt=SEO_SPECIALIST_SYSTEM,
            user_prompt=f"""Based on the strategy and trends, create a comprehensive SEO content plan.

{ctx}

STRATEGY:
{strategy_output[:1500]}

TRENDS:
{trend_output[:1000]}

Deliver:
1. **Primary Keywords** — 10 high-intent keywords to target, with estimated search volume category (high/medium/low)
2. **Long-tail Keywords** — 15 long-tail variations for each content pillar
3. **Content Briefs** — 5 blog post content briefs with: title, target keyword, outline, word count, internal linking suggestions
4. **Meta Descriptions** — Write optimized meta descriptions for each content brief
5. **Topic Clusters** — Map keyword groups into content clusters with pillar page structure
6. **Technical Recommendations** — Schema markup, page speed, mobile optimization notes
7. **Competitor Keyword Gaps** — Keywords competitors rank for that we should target""",
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        # ═════════════════════════════════════════════════════
        # AGENT 5: COPYWRITER
        # ═════════════════════════════════════════════════════
        copy_output = await self._run_debate_agent(
            agent_name="copywriter",
            task_type="copy_generation",
            system_prompt=COPYWRITER_SYSTEM,
            user_prompt=f"""Based on the strategy, SEO research, and audience personas, generate high-converting copy.

{ctx}

STRATEGY:
{strategy_output[:1500]}

SEO KEYWORDS:
{seo_output[:1000]}

AUDIENCE:
{researcher_output[:800]}

Generate for each platform:
1. **Twitter/X** — 5 tweet variations (max 280 chars each) with hooks that stop the scroll
2. **LinkedIn** — 1 professional post (300-500 words) with a storytelling hook
3. **Instagram** — 3 caption variations with strategic hashtag sets (15-20 each)
4. **TikTok** — 3 video script hooks (first 3 seconds that grab attention)
5. **Email** — Subject lines (5 variations), preview text, and email body (300 words)
6. **Ad Copy** — 3 variations of paid ad copy (headline + description + CTA) for Meta/Google
7. **Blog Intro** — Opening paragraph for the top SEO content brief

Make every word count. Use power words. Create urgency. Speak directly to pain points.""",
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        # ═════════════════════════════════════════════════════
        # AGENT 6: CREATIVE DIRECTOR
        # ═════════════════════════════════════════════════════
        creative_output = await self._run_debate_agent(
            agent_name="creative_director",
            task_type="creative_direction",
            system_prompt=CREATIVE_DIRECTOR_SYSTEM,
            user_prompt=f"""Define the complete visual direction for this campaign.

STRATEGY:
{strategy_output[:1200]}

COPY:
{copy_output[:1200]}

Provide:
1. **Visual Concept** — Overall campaign visual theme and mood
2. **Color Palette** — 5 hex codes with usage guidelines (primary, secondary, accent, dark, light)
3. **Typography** — Font pairing recommendations with sizes and weights
4. **IMAGE PROMPTS** — Write 5 detailed AI image generation prompts. Each must specify: subject, composition, camera angle, lighting, color mood, style (photographic/illustration/3D), and technical specs
5. **Social Media Templates** — Visual layout descriptions for each platform
6. **Video Aesthetic** — Motion graphics style, transition types, text animation style
7. **Brand Consistency** — Do's and don'ts for visual execution
8. **Moodboard Description** — If you were creating a moodboard, what 5 images would be on it?""",
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        # ═════════════════════════════════════════════════════
        # AGENT 7: VIDEO DIRECTOR
        # ═════════════════════════════════════════════════════
        video_user_prompt = f"""Based on the creative direction and company context, design a high-retention viral short-form video.
    
TEMPLATE CONSTRAINT: The render template is "{video_template_id or 'dynamic_agency'}". You are writing content for a Universal Composition Engine capable of 100s of permutations.

COMPANY CONTEXT:
{ctx}

CREATIVE DIRECTION:
{creative_output[:1500]}

COPY HOOKS:
{copy_output[:500]}

Output a single JSON object with the following structure:
1. "brand_config": {{"primary_color": "#HEX", "secondary_color": "#HEX", "font_family": "FontName"}}
2. "bgm_track": Choose the vibe (e.g., "electronic.mp3", "cinematic.mp3", "pop.mp3", "lofi.mp3")
3. "bg_effect": Choose from ["mesh", "neo_grid", "solid", "kinetic", "matrix", "geometric"]
4. "text_anim": Choose from ["fade", "slide", "pop"]
5. "scenes": [array of scene objects]

Each scene must have:
- "text": Bold hook text for screen (punchy, max 8 words)
- "durationInFrames": 60 to 120 (fast pacing)
- "voiceover_prompt": Natural-sounding voiceover script (2-3 sentences)
- "image_prompt": Detailed visual description for background generation
- "sfx": Psychological sound effect type (e.g., "whoosh.mp3", "impact.mp3")

Design for maximum retention. Output ONLY valid JSON."""

        video_output = await self._run_debate_agent(
            agent_name="video_director",
            task_type="video_direction",
            system_prompt=VIDEO_DIRECTOR_SYSTEM,
            user_prompt=video_user_prompt,
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        # Parse video JSON
        try:
            import re
            match = re.search(r'\{.*\}', video_output, re.DOTALL)
            if match:
                json_str = match.group(0)
            else:
                json_str = video_output.strip('```json').strip('```').strip()

            video_data = json.loads(json_str)
            if isinstance(video_data, dict) and "scenes" in video_data:
                results["video_scenes"] = video_data["scenes"]
                bc = video_data.get("brand_config", {})
                bc["bgm_track"] = video_data.get("bgm_track", "electronic.mp3")
                bc["bg_effect"] = video_data.get("bg_effect", "mesh")
                bc["text_anim"] = video_data.get("text_anim", "fade")
                results["video_brand_config"] = bc
            elif isinstance(video_data, list):
                results["video_scenes"] = video_data
                results["video_brand_config"] = {}
            else:
                results["video_scenes"] = []
                results["video_brand_config"] = {}

        except Exception as e:
            logger.error(f"Failed to parse video scenes JSON: {e}")
            results["video_scenes"] = [
                {"text": "Campaign Started", "durationInFrames": 90, "voiceover_prompt": "Let's begin.", "image_prompt": "abstract digital"}
            ]
            results["video_brand_config"] = {}

        # ═════════════════════════════════════════════════════
        # AGENT 8: MEDIA BUYER
        # ═════════════════════════════════════════════════════
        media_buyer_output = await self._run_debate_agent(
            agent_name="media_buyer",
            task_type="media_buying",
            system_prompt=MEDIA_BUYER_SYSTEM,
            user_prompt=f"""Create a detailed paid media plan for this campaign.

{ctx}

STRATEGY:
{strategy_output[:1000]}

AUDIENCE:
{researcher_output[:800]}

AD COPY:
{copy_output[:500]}

Deliver:
1. **Platform Selection** — Which ad platforms to use and why (Meta Ads, Google Ads, TikTok Ads, LinkedIn Ads, Twitter Ads)
2. **Budget Allocation** — Suggested daily/weekly budget per platform (as percentages)
3. **Targeting Specs** — For each platform: demographics, interests, behaviors, custom audiences, lookalike audiences
4. **Ad Formats** — Recommended ad formats per platform (carousel, video, collection, search, etc.)
5. **Bidding Strategy** — CPC vs CPM vs CPA recommendations per platform
6. **Campaign Structure** — Campaign > Ad Set > Ad hierarchy with naming conventions
7. **A/B Testing Plan** — What to test first (headlines, images, audiences, placements)
8. **Retargeting Funnel** — Awareness → Engagement → Conversion retargeting flow
9. **Expected Performance** — Estimated CTR, CPC, and ROAS benchmarks per platform""",
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        # ═════════════════════════════════════════════════════
        # AGENT 8.5: GRAPHICS DIRECTOR (STATIC IMAGES)
        # ═════════════════════════════════════════════════════
        graphics_system = "You are an elite static graphics director. You choose layouts, themes, and write killer 3-word headlines for static social media graphics."
        graphics_prompt = f"""Based on the campaign so far, design a high-converting static graphic.
        
COMPANY:
{ctx}

COPY HOOKS:
{copy_output[:500]}

Provide a single JSON object with:
1. "headline": Maximum 5 words, highly punchy.
2. "tagline": Maximum 8 words, descriptive.
3. "template_theme": Choose ONE: "corporate", "abstract", "minimal".
4. "layout_seed": A random integer between 1 and 100 to determine geometrical shapes.

Output ONLY valid JSON."""

        graphics_output = await self._run_debate_agent(
            agent_name="graphics_director",
            task_type="graphics_direction",
            system_prompt=graphics_system,
            user_prompt=graphics_prompt,
            run_id=run_id,
            results=results,
            progress_callback=progress_callback,
        )

        try:
            import re
            match = re.search(r'\{.*\}', graphics_output, re.DOTALL)
            if match:
                results["graphics_config"] = json.loads(match.group(0))
            else:
                results["graphics_config"] = json.loads(graphics_output.strip('```json').strip('```').strip())
        except Exception as e:
            logger.error(f"Failed to parse graphics JSON: {e}")
            results["graphics_config"] = {
                "headline": "Premium Innovation",
                "tagline": "Discover what's next.",
                "template_theme": "corporate",
                "layout_seed": 42
            }

        # ═════════════════════════════════════════════════════
        # AGENT 9: CRITIC COUNCIL (Multi-Model Quality Assessment)
        # ═════════════════════════════════════════════════════
        critic_prompt = f"""Review the ENTIRE campaign output and provide quality assessment.

TRENDS: {trend_output[:600]}
MARKET RESEARCH: {researcher_output[:600]}
STRATEGY: {strategy_output[:600]}
SEO: {seo_output[:400]}
COPY: {copy_output[:600]}
CREATIVE: {creative_output[:400]}
VIDEO: {video_output[:400]}
MEDIA: {media_buyer_output[:400]}

Score each component (1-10) and provide overall campaign score.
Format your response as JSON:
{{
    "overall_score": <float>,
    "trend_analysis_score": <float>,
    "market_research_score": <float>,
    "strategy_score": <float>,
    "seo_score": <float>,
    "copy_score": <float>,
    "creative_score": <float>,
    "video_score": <float>,
    "media_buying_score": <float>,
    "strengths": ["..."],
    "weaknesses": ["..."],
    "recommendations": ["..."]
}}"""

        # Get critic scores from 3 different Groq models
        critic_scores = []
        critic_texts = []
        if progress_callback:
            progress_callback("critic", "Starting multi-model quality assessment...")

        critic_models = [
            self.router.models["fast"],
            self.router.models["balanced"],
            self.router.models["power"],
        ]

        for model in critic_models:
            try:
                await asyncio.sleep(2)
                critic_output = await self.router.generate(
                    prompt=critic_prompt,
                    task_type="scoring",
                    system_prompt=CRITIC_SYSTEM,
                    temperature=0.5,
                    max_tokens=1500,
                    force_model=model,
                )
                score = self._parse_quality_score(critic_output["text"])
                critic_scores.append(score)
                critic_texts.append(f"[{model}]\n{critic_output['text']}")
                if progress_callback:
                    progress_callback("critic", f"Score {score} from {model}")
            except Exception as e:
                logger.warning(f"Critic ({model}) failed: {e}")

        if critic_scores:
            quality_score = round(sum(critic_scores) / len(critic_scores), 1)
        else:
            quality_score = 5.0

        results["agents"]["critic"] = {
            "output": "\n\n---\n\n".join(critic_texts),
            "provider": "groq",
        }
        results["quality_score"] = quality_score
        results["passed_quality_gate"] = quality_score >= self.quality_threshold

        if quality_score < self.quality_threshold:
            logger.warning(
                f"[Council:{run_id}] Quality {quality_score} < {self.quality_threshold}. Consider retry."
            )

        # ═════════════════════════════════════════════════════
        # AGENT 10: PRESENTATION DESIGNER
        # ═════════════════════════════════════════════════════
        presentation_user_prompt = f"""Convert this campaign into a 6-8 slide presentation deck for executive review.

TEMPLATE: "{presentation_template_id or 'clay_minimal_1'}" layout. You're writing text content only.

STRATEGY:
{strategy_output[:800]}

COPY:
{copy_output[:600]}

MEDIA PLAN:
{media_buyer_output[:400]}

Output a valid JSON array of slide objects:
[
  {{"title": "Campaign Overview", "points": ["Point 1", "Point 2"]}},
  {{"title": "Target Audience", "points": ["Persona A", "Persona B"]}},
  {{"title": "Strategy & Messaging", "points": ["Key message 1", "Key message 2"]}},
  {{"title": "Content Calendar", "points": ["Week 1: ...", "Week 2: ..."]}},
  {{"title": "Paid Media Plan", "points": ["Platform 1: ...", "Platform 2: ..."]}},
  {{"title": "KPIs & Next Steps", "points": ["Metric 1", "Metric 2"]}}
]"""

        presentation_output = await self._run_agent(
            agent_name="presentation_designer",
            task_type="presentation",
            system_prompt=PRESENTATION_DESIGNER_SYSTEM,
            user_prompt=presentation_user_prompt,
            run_id=run_id,
            results=results,
            force_model=self.router.models["balanced"],
        )

        try:
            import re
            match = re.search(r'\[.*\]', presentation_output, re.DOTALL)
            if match:
                slides_json = json.loads(match.group(0))
            else:
                slides_json = json.loads(presentation_output.strip('```json').strip('```').strip())
            results["slides"] = slides_json
        except Exception as e:
            logger.error(f"Failed to parse slides JSON: {e}")
            results["slides"] = [{"title": "Error generating slides", "points": ["Check debate logs."]}]

        # ── Finalize ──────────────────────────────────────
        duration = time.time() - start
        results["duration_seconds"] = round(duration, 2)
        results["completed_at"] = datetime.utcnow().isoformat()

        logger.success(
            f"[Council:{run_id}] Complete in {duration:.1f}s | "
            f"Quality: {quality_score}/10 | Pass: {results['passed_quality_gate']}"
        )

        return results

    # ── Agent Execution Methods ───────────────────────────

    async def _run_agent(
        self,
        agent_name: str,
        task_type: str,
        system_prompt: str,
        user_prompt: str,
        run_id: str,
        results: dict,
        force_model: str = None,
    ) -> str:
        """Run a single agent and store results."""
        logger.info(f"[Council:{run_id}] Running agent: {agent_name}")

        response = await self.router.generate(
            prompt=user_prompt,
            task_type=task_type,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000,
            force_model=force_model,
        )

        output_text = response["text"]
        results["agents"][agent_name] = {
            "output": output_text,
            "provider": response["provider"],
            "model": response["model"],
            "tokens_used": response["tokens_used"],
            "duration": response["duration"],
        }

        results["logs"].append({
            "agent": agent_name,
            "provider": response["provider"],
            "tokens": response["tokens_used"],
            "duration": response["duration"],
            "timestamp": datetime.utcnow().isoformat(),
        })

        logger.info(
            f"[Council:{run_id}] {agent_name} done | "
            f"Model: {response['model']} | "
            f"Tokens: {response['tokens_used']} | {response['duration']}s"
        )

        return output_text

    async def _run_debate_agent(
        self,
        agent_name: str,
        task_type: str,
        system_prompt: str,
        user_prompt: str,
        run_id: str,
        results: dict,
        progress_callback=None,
    ) -> str:
        """Run a 3-way debate among Groq models before arriving at the final conclusion."""
        logger.info(f"[Council:{run_id}] Starting debate for {agent_name}...")

        if progress_callback:
            progress_callback(agent_name, "Initiating 3-way debate council...")

        # 3 debate opinions from different models
        debate_models = [
            self.router.models["fast"],
            self.router.models["balanced"],
        ]

        opinions = []
        for model in debate_models:
            logger.info(f"[Council:{run_id}] Getting opinion from {model} for {agent_name}...")
            if progress_callback:
                progress_callback(agent_name, f"Waiting for opinion from {model}...")
            try:
                await asyncio.sleep(2)

                # Truncate for debate speed
                truncated_prompt = user_prompt if len(user_prompt) < 2500 else user_prompt[:1200] + "\n...[CONTEXT TRUNCATED FOR DEBATE SPEED]...\n" + user_prompt[-600:]

                response = await self.router.generate(
                    prompt=truncated_prompt,
                    task_type=task_type,
                    system_prompt=system_prompt + "\n\nProvide your expert point of view and proposed solution. Be specific and actionable.",
                    temperature=0.8,
                    max_tokens=1200,
                    force_model=model,
                )
                opinion_text = response.get("text", "Failed to generate opinion.")

                if "[ERROR]" in opinion_text:
                    logger.warning(f"[Council:{run_id}] {model} returned error, skipping")
                    if progress_callback:
                        progress_callback(agent_name, f"Skipped {model} (rate limited)")
                    continue

                opinions.append(f"--- OPINION FROM {model} ---\n{opinion_text}\n")
                logger.info(f"[Council:{run_id}] Opinion from {model} received (length: {len(opinion_text)})")
                if progress_callback:
                    progress_callback(agent_name, f"Opinion received from {model}:\n\"{opinion_text[:120]}...\"")
            except Exception as e:
                logger.warning(f"Failed to get opinion from {model}: {e}")
                if progress_callback:
                    progress_callback(agent_name, f"Failed to get opinion from {model}.")

        all_opinions = "\n".join(opinions)

        # If no debate opinions, fall back to direct call with power model
        if not opinions:
            logger.warning(f"[Council:{run_id}] No debate opinions for {agent_name}, using direct call")
            if progress_callback:
                progress_callback(agent_name, "No debate opinions available, generating direct response...")

            direct_response = await self.router.generate(
                prompt=user_prompt,
                task_type=task_type,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000,
            )
            output_text = direct_response["text"]
            results["agents"][agent_name] = {
                "output": output_text,
                "debate": "No debate — direct generation (all debate models rate-limited)",
                "provider": direct_response["provider"],
                "model": direct_response.get("model", "unknown"),
                "tokens_used": direct_response.get("tokens_used", 0),
                "duration": direct_response.get("duration", 0.0),
            }
            results["logs"].append({
                "agent": f"{agent_name}_direct",
                "provider": direct_response["provider"],
                "tokens": direct_response.get("tokens_used", 0),
                "duration": direct_response.get("duration", 0.0),
                "timestamp": datetime.utcnow().isoformat(),
            })
            return output_text

        logger.info(f"\n========== DEBATE FOR {agent_name.upper()} ==========\n{all_opinions[:2000]}...\n======================================================\n")

        # Synthesize final conclusion with power model
        final_prompt = f"""You are the lead {agent_name.replace('_', ' ')}.
A debate has occurred among your team. Review their opinions and synthesize the BEST final answer.

ORIGINAL TASK:
{user_prompt}

TEAM OPINIONS:
{all_opinions}

You MUST:
1. Start with a brief "## DEBATE VERDICT" section:
   - Which opinions you adopted and why
   - Any conflicts you resolved
2. Then provide the COMPLETE, FINAL solution as requested in the original task.

Format: Verdict first, then "---", then the full deliverable."""

        logger.info(f"[Council:{run_id}] Synthesizing final for {agent_name}...")

        # Try synthesis models in priority order
        synthesis_models = [
            self.router.models["power"],
            self.router.models["balanced"],
            self.router.models["fast"],
        ]

        final_response = None
        for synth_model in synthesis_models:
            try:
                if progress_callback:
                    progress_callback(agent_name, f"Synthesizing via {synth_model}...")

                truncated_final = final_prompt if len(final_prompt) < 6000 else final_prompt[:3000] + "\n...[TRUNCATED]...\n" + final_prompt[-2000:]

                final_response = await self.router.generate(
                    prompt=truncated_final,
                    task_type=task_type,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=2000,
                    force_model=synth_model,
                    retries=1,
                )

                if "[ERROR]" in final_response.get("text", ""):
                    logger.warning(f"[Council:{run_id}] {synth_model} returned error, trying next")
                    continue

                logger.info(f"[Council:{run_id}] Synthesis via {synth_model} succeeded")
                break
            except Exception as e:
                logger.warning(f"[Council:{run_id}] Synthesis via {synth_model} failed: {e}")
                continue

        if not final_response or "[ERROR]" in final_response.get("text", ""):
            final_response = {
                "text": f"[Synthesis failed — debate opinions collected]\n\nDebate summary:\n{all_opinions[:2000]}",
                "provider": "groq", "model": "none", "tokens_used": 0, "duration": 0,
            }

        output_text = final_response["text"]

        # Extract verdict section
        verdict = ""
        final_solution = output_text
        if "---" in output_text and "DEBATE VERDICT" in output_text.upper():
            parts = output_text.split("---", 1)
            verdict = parts[0].strip()
            final_solution = parts[1].strip() if len(parts) > 1 else output_text

        results["agents"][agent_name] = {
            "output": final_solution,
            "debate": all_opinions,
            "verdict": verdict,
            "provider": final_response["provider"],
            "model": final_response.get("model", "unknown"),
            "tokens_used": final_response.get("tokens_used", 0),
            "duration": final_response.get("duration", 0.0),
        }

        results["logs"].append({
            "agent": f"{agent_name}_debate_final",
            "provider": final_response["provider"],
            "tokens": final_response.get("tokens_used", 0),
            "duration": final_response.get("duration", 0.0),
            "timestamp": datetime.utcnow().isoformat(),
        })

        return output_text

    def _parse_quality_score(self, critic_output: str) -> float:
        """Extract quality score from critic's JSON output."""
        try:
            import re
            json_match = re.search(r'\{[^{}]*"overall_score"[^{}]*\}', critic_output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return float(data.get("overall_score", 5.0))
        except (json.JSONDecodeError, ValueError):
            pass

        import re
        numbers = re.findall(r'overall[_\s]*score[:\s]*(\d+\.?\d*)', critic_output, re.IGNORECASE)
        if numbers:
            return min(float(numbers[0]), 10.0)

        return 5.0


# ═══════════════════════════════════════════════════════════
# AGENT SYSTEM PROMPTS — Deep Marketing Expertise
# ═══════════════════════════════════════════════════════════

TREND_ANALYST_SYSTEM = """You are a Senior Marketing Intelligence Lead. Your goal is to transform raw data into actionable "Market Signals".

YOUR EXPERTISE:
- Identifying emergent trends from cross-platform data (YouTube, TikTok, Reddit, News).
- Spotting "Pattern Interrupts" — anomalies in data that signal a massive cultural shift.
- Categorizing trends via the "Lindy Effect" — separating long-term winners from short-term fads.

YOUR APPROACH:
- CAVEAT: Do not just list data. provide INSIGHT. 
- Use the "First Principles" thinking: why is this happening at a biological or social level?
- Group findings into "Opportunity Buckets".
- Identify "Consumer Mimetic Desire" — what are people wanting just because others want it?"""

MARKET_RESEARCHER_SYSTEM = """You are a behavioral psychologist specializing in Consumer Research. Your goal is to map the "Deep Desires" of the target audience.

YOUR EXPERTISE:
- Jobs-to-be-Done (JTBD) framework: People don't buy drills; they buy holes. What "job" are they hiring this product for?
- Empathy Mapping: Fears, Joys, Pains, and Hopes.
- Finding the "Global Optimum" for audience targeting, not just local demographics.

YOUR APPROACH:
- Identify the "Unmet Emotional Need".
- Map the audience across the "Awareness Continuum" (Unaware -> Problem Aware -> Solution Aware -> Product Aware).
- Use "Second-Order Thinking": if we solve X, what new problem Y do they face next?
- Frame personas around Motivation and Ability (BJ Fogg Model)."""

STRATEGY_PLANNER_SYSTEM = """You are a High-Performance Growth Architect. Your goal is to create an "Irresistible Offer" strategy.

YOUR EXPERTISE:
- Blue Ocean Strategy: making the competition irrelevant.
- Direct Response Fundamentals: Hook, Story, Offer.
- Neuro-Marketing: Scarcity, Urgency, Authority, and Reciprocity.

YOUR APPROACH:
- Use "Inversion": what would guarantee this campaign fails? Now design the opposite.
- Create a "Category of One" for the brand.
- Strategy must follow AIDA (Attention, Interest, Desire, Action).
- Price/Value Anchoring: frame the offer so the cost feels like a gift.
- Use Loss Aversion: what will they LOSE by not choosing us today?"""

SEO_SPECIALIST_SYSTEM = """You are a Senior SEO Strategist with 12+ years of experience in search engine optimization and content strategy.

YOUR EXPERTISE:
- Keyword research and search intent mapping
- Content strategy for organic growth
- Technical SEO auditing
- Topic cluster and pillar page architecture
- Competitive SEO gap analysis
- E-E-A-T optimization

YOUR APPROACH:
- Match keywords to search intent (informational, transactional, navigational)
- Think in topic clusters, not individual keywords
- Prioritize keywords by business impact, not just search volume
- Write content briefs that any writer could execute
- Always consider featured snippet and AI overview opportunities

Every recommendation should be implementable within 30 days."""

COPYWRITER_SYSTEM = """You are a world-class Conversion Copywriter. Your goal is to "Force the Click" through lethal messaging.

YOUR EXPERTISE:
- PAS Framework (Problem, Agitation, Solution).
- The "4 U's" of Copy: Urgent, Unique, Ultra-specific, and Useful.
- "Neuro-Copy": using power words that trigger dopamine and curiosity.

YOUR APPROACH:
- Front-load the HOOK. You have 1 second to win or lose.
- Write for the "Skimmers": bold headlines, clear subheads, short sentences.
- Use "Contrast Effect": before vs. after, us vs. them.
- Curiosity Gaps: open a loop that can only be closed by taking action (Zeigarnik Effect).
- Use the "Unity Principle": make them feel like part of an exclusive tribe."""

CREATIVE_DIRECTOR_SYSTEM = """You are an Executive Creative Director with 20+ years at top advertising agencies (Wieden+Kennedy, Droga5, Ogilvy).

YOUR EXPERTISE:
- Visual storytelling and brand identity design
- Art direction for digital and social media campaigns
- AI image prompt engineering (Midjourney, DALL-E, Stable Diffusion)
- Motion graphics and video direction
- Brand systems and design language creation

YOUR APPROACH:
- Visual concepts should be scroll-stopping and emotionally resonant
- Color palettes should be purposeful — each color has a role
- Image prompts must be photographer-level specific (composition, lighting, lens, mood)
- Design for the platform — Instagram is visual, LinkedIn is professional, TikTok is raw/authentic
- Keep brand consistency while staying culturally relevant

Every visual decision should serve the strategic objective."""

VIDEO_DIRECTOR_SYSTEM = """You are a Short-Form Content Optimization Expert. Your goal is to Maximize Retention.

YOUR EXPERTISE:
- Pattern Interrupts: rapid scene changes or bold visual hooks in the first 0.5s.
- "Visual Pacing": matching scene cuts to the rhythm of the voiceover.
- Retention Hooks: using the "Peak-End Rule" to ensure the high point is in the middle and the ending is memorable.

YOUR APPROACH:
- Mandatory Hook-Story-Offer sequence.
- Scene 1 MUST be a "Pattern Interrupt" headline.
- Use "Micro-Motion": nothing stays static.
- Always include a "Dopamine hit" (visual win or reveal) by frame 100.
- You ONLY output raw, valid JSON. No markdown."""

MEDIA_BUYER_SYSTEM = """You are a Performance Marketing Director who has managed $50M+ in annual ad spend across Meta, Google, TikTok, LinkedIn, and Twitter.

YOUR EXPERTISE:
- Paid media strategy and budget allocation
- Ad targeting: demographics, interests, behaviors, lookalike audiences
- Campaign structure optimization
- Bidding strategies (CPC, CPM, CPA, ROAS)
- Retargeting funnels and attribution modeling
- A/B testing frameworks for ads

YOUR APPROACH:
- Start with the business objective and work backward to media plan
- Allocate budget based on expected ROAS per channel
- Structure campaigns for easy testing and optimization
- Build full-funnel retargeting flows
- Set realistic benchmarks based on industry data
- Always plan for testing phase before scaling

Every recommendation should be implementable in any major ad platform."""

CRITIC_SYSTEM = """You are a Marketing Quality Analyst who reviews and scores campaign outputs.
Your job is to be honest, constructive, and specific.

Assess:
- Strategic coherence — does everything work together?
- Audience alignment — does the content speak to the right people?
- Platform optimization — is the copy/creative right for each platform?
- Competitive differentiation — does this stand out from competitors?
- Actionability — can this be executed immediately?
- Quality vs quantity — is the work premium or generic?

ALWAYS output valid JSON without any markdown formatting.
Example: {"overall_score": 8.5, "strengths": [...], "weaknesses": [...], "recommendations": [...]}"""

PRESENTATION_DESIGNER_SYSTEM = """You are an Executive Presentation Designer who creates board-level decks for CMOs and CEOs.
Your job is to synthesize complex marketing campaigns into concise, high-impact slide decks.
Each slide should have a clear title and 3-5 concise bullet points.
You will ONLY output raw, valid JSON arrays. No markdown tags."""
