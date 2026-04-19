"""
Generate template seed data for the design studio.
Creates 50+ image templates and 20 video templates in the database.

Run with: python backend/scripts/generate_templates.py
"""
import os
import sys
import json
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage.database import init_db, get_session_direct, Template
from loguru import logger


# ── Image Templates Configuration ─────────────────────────

IMAGE_TEMPLATES = [
    # Twitter Posts (1200x675) - 10 templates
    {"id": "img-twitter-001", "name": "Twitter Post - Bold Announcement", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 0, "theme": "corporate", "tags": ["bold", "announcement", "professional"]},
    {"id": "img-twitter-002", "name": "Twitter Post - Minimal Quote", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 10, "theme": "minimal", "tags": ["minimal", "quote", "clean"]},
    {"id": "img-twitter-003", "name": "Twitter Post - Abstract Art", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 20, "theme": "abstract", "tags": ["abstract", "creative", "artistic"]},
    {"id": "img-twitter-004", "name": "Twitter Post - Neon Glow", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 30, "theme": "neon", "tags": ["neon", "glow", "eye-catching"]},
    {"id": "img-twitter-005", "name": "Twitter Post - Luxury Brand", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 40, "theme": "luxury", "tags": ["luxury", "premium", "elegant"]},
    {"id": "img-twitter-006", "name": "Twitter Post - Product Feature", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 3, "theme": "corporate", "tags": ["product", "feature", "showcase"]},
    {"id": "img-twitter-007", "name": "Twitter Post - Event Promo", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 15, "theme": "abstract", "tags": ["event", "promo", "dynamic"]},
    {"id": "img-twitter-008", "name": "Twitter Post - Sale Alert", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 33, "theme": "neon", "tags": ["sale", "alert", "urgent"]},
    {"id": "img-twitter-009", "name": "Twitter Post - Team Update", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 1, "theme": "corporate", "tags": ["team", "update", "corporate"]},
    {"id": "img-twitter-010", "name": "Twitter Post - Tech Launch", "category": "twitter", "width": 1200, "height": 675, "layout_seed": 35, "theme": "neon", "tags": ["tech", "launch", "innovation"]},

    # Instagram Posts (1080x1080) - 10 templates
    {"id": "img-instagram-001", "name": "Instagram Post - Editorial Split", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 0, "theme": "corporate", "tags": ["editorial", "split", "professional"]},
    {"id": "img-instagram-002", "name": "Instagram Post - Minimal Zen", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 10, "theme": "minimal", "tags": ["minimal", "zen", "peaceful"]},
    {"id": "img-instagram-003", "name": "Instagram Post - Abstract Pop", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 24, "theme": "abstract", "tags": ["abstract", "pop", "colorful"]},
    {"id": "img-instagram-004", "name": "Instagram Post - Neon Matrix", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 33, "theme": "neon", "tags": ["neon", "matrix", "cyber"]},
    {"id": "img-instagram-005", "name": "Instagram Post - Gold Premium", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 41, "theme": "luxury", "tags": ["luxury", "gold", "premium"]},
    {"id": "img-instagram-006", "name": "Instagram Post - Fashion Forward", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 42, "theme": "luxury", "tags": ["fashion", "trendy", "stylish"]},
    {"id": "img-instagram-007", "name": "Instagram Post - Product Grid", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 5, "theme": "corporate", "tags": ["product", "grid", "catalog"]},
    {"id": "img-instagram-008", "name": "Instagram Post - Quote Card", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 12, "theme": "minimal", "tags": ["quote", "inspirational", "text"]},
    {"id": "img-instagram-009", "name": "Instagram Post - Carousel Cover", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 22, "theme": "abstract", "tags": ["carousel", "cover", "series"]},
    {"id": "img-instagram-010", "name": "Instagram Post - Behind Scenes", "category": "instagram", "width": 1080, "height": 1080, "layout_seed": 18, "theme": "minimal", "tags": ["bts", "authentic", "candid"]},

    # Instagram Stories (1080x1920) - 10 templates
    {"id": "img-story-001", "name": "Instagram Story - Vertical Hero", "category": "story", "width": 1080, "height": 1920, "layout_seed": 0, "theme": "corporate", "tags": ["hero", "vertical", "impact"]},
    {"id": "img-story-002", "name": "Instagram Story - Minimal Space", "category": "story", "width": 1080, "height": 1920, "layout_seed": 11, "theme": "minimal", "tags": ["minimal", "space", "airy"]},
    {"id": "img-story-003", "name": "Instagram Story - Abstract Wave", "category": "story", "width": 1080, "height": 1920, "layout_seed": 28, "theme": "abstract", "tags": ["wave", "flow", "dynamic"]},
    {"id": "img-story-004", "name": "Instagram Story - Neon Pulse", "category": "story", "width": 1080, "height": 1920, "layout_seed": 34, "theme": "neon", "tags": ["pulse", "energy", "vibrant"]},
    {"id": "img-story-005", "name": "Instagram Story - Elegant Vertical", "category": "story", "width": 1080, "height": 1920, "layout_seed": 40, "theme": "luxury", "tags": ["elegant", "sophisticated", "vertical"]},
    {"id": "img-story-006", "name": "Instagram Story - Swipe Up CTA", "category": "story", "width": 1080, "height": 1920, "layout_seed": 4, "theme": "corporate", "tags": ["cta", "swipe", "action"]},
    {"id": "img-story-007", "name": "Instagram Story - Poll Interactive", "category": "story", "width": 1080, "height": 1920, "layout_seed": 16, "theme": "abstract", "tags": ["poll", "interactive", "engagement"]},
    {"id": "img-story-008", "name": "Instagram Story - Countdown", "category": "story", "width": 1080, "height": 1920, "layout_seed": 32, "theme": "neon", "tags": ["countdown", "urgent", "launch"]},
    {"id": "img-story-009", "name": "Instagram Story - Testimonial", "category": "story", "width": 1080, "height": 1920, "layout_seed": 13, "theme": "minimal", "tags": ["testimonial", "review", "social-proof"]},
    {"id": "img-story-010", "name": "Instagram Story - Flash Sale", "category": "story", "width": 1080, "height": 1920, "layout_seed": 36, "theme": "neon", "tags": ["sale", "flash", "limited"]},

    # LinkedIn Posts (1200x627) - 5 templates
    {"id": "img-linkedin-001", "name": "LinkedIn Post - Professional Update", "category": "linkedin", "width": 1200, "height": 627, "layout_seed": 0, "theme": "corporate", "tags": ["professional", "update", "business"]},
    {"id": "img-linkedin-002", "name": "LinkedIn Post - Company News", "category": "linkedin", "width": 1200, "height": 627, "layout_seed": 1, "theme": "corporate", "tags": ["news", "company", "announcement"]},
    {"id": "img-linkedin-003", "name": "LinkedIn Post - Thought Leadership", "category": "linkedin", "width": 1200, "height": 627, "layout_seed": 10, "theme": "minimal", "tags": ["thought-leadership", "insights", "expert"]},
    {"id": "img-linkedin-004", "name": "LinkedIn Post - Case Study", "category": "linkedin", "width": 1200, "height": 627, "layout_seed": 3, "theme": "corporate", "tags": ["case-study", "results", "data"]},
    {"id": "img-linkedin-005", "name": "LinkedIn Post - Hiring Now", "category": "linkedin", "width": 1200, "height": 627, "layout_seed": 5, "theme": "corporate", "tags": ["hiring", "careers", "jobs"]},

    # YouTube Thumbnails (1280x720) - 5 templates
    {"id": "img-youtube-001", "name": "YouTube Thumbnail - Bold Title", "category": "youtube", "width": 1280, "height": 720, "layout_seed": 0, "theme": "corporate", "tags": ["bold", "title", "clickable"]},
    {"id": "img-youtube-002", "name": "YouTube Thumbnail - Face + Text", "category": "youtube", "width": 1280, "height": 720, "layout_seed": 1, "theme": "abstract", "tags": ["face", "text", "engagement"]},
    {"id": "img-youtube-003", "name": "YouTube Thumbnail - Neon Glow", "category": "youtube", "width": 1280, "height": 720, "layout_seed": 30, "theme": "neon", "tags": ["neon", "glow", "eye-catching"]},
    {"id": "img-youtube-004", "name": "YouTube Thumbnail - Product Review", "category": "youtube", "width": 1280, "height": 720, "layout_seed": 3, "theme": "corporate", "tags": ["product", "review", "comparison"]},
    {"id": "img-youtube-005", "name": "YouTube Thumbnail - Tutorial", "category": "youtube", "width": 1280, "height": 720, "layout_seed": 10, "theme": "minimal", "tags": ["tutorial", "how-to", "educational"]},

    # Product Showcases (Various) - 10 templates
    {"id": "img-product-001", "name": "Product Showcase - Hero Shot", "category": "product", "width": 1080, "height": 1350, "layout_seed": 0, "theme": "corporate", "tags": ["hero", "product", "showcase"]},
    {"id": "img-product-002", "name": "Product Showcase - Flat Lay", "category": "product", "width": 1080, "height": 1080, "layout_seed": 10, "theme": "minimal", "tags": ["flat-lay", "clean", "arrangement"]},
    {"id": "img-product-003", "name": "Product Showcase - Lifestyle", "category": "product", "width": 1080, "height": 1350, "layout_seed": 20, "theme": "abstract", "tags": ["lifestyle", "context", "real-world"]},
    {"id": "img-product-004", "name": "Product Showcase - Detail Close-up", "category": "product", "width": 1080, "height": 1080, "layout_seed": 41, "theme": "luxury", "tags": ["detail", "close-up", "quality"]},
    {"id": "img-product-005", "name": "Product Showcase - Comparison", "category": "product", "width": 1200, "height": 675, "layout_seed": 1, "theme": "corporate", "tags": ["comparison", "before-after", "features"]},
    {"id": "img-product-006", "name": "Product Showcase - Collection Grid", "category": "product", "width": 1080, "height": 1080, "layout_seed": 5, "theme": "minimal", "tags": ["collection", "grid", "catalog"]},
    {"id": "img-product-007", "name": "Product Showcase - Neon Highlight", "category": "product", "width": 1080, "height": 1350, "layout_seed": 30, "theme": "neon", "tags": ["neon", "highlight", "modern"]},
    {"id": "img-product-008", "name": "Product Showcase - Premium Gold", "category": "product", "width": 1080, "height": 1350, "layout_seed": 42, "theme": "luxury", "tags": ["premium", "gold", "luxury"]},
    {"id": "img-product-009", "name": "Product Showcase - Feature Callout", "category": "product", "width": 1200, "height": 627, "layout_seed": 3, "theme": "corporate", "tags": ["feature", "callout", "benefits"]},
    {"id": "img-product-010", "name": "Product Showcase - Abstract Background", "category": "product", "width": 1080, "height": 1080, "layout_seed": 24, "theme": "abstract", "tags": ["abstract", "creative", "artistic"]},
]


# ── Video Templates Configuration ─────────────────────────

VIDEO_TEMPLATES = [
    # Existing Remotion Engines
    {"id": "vid-dynamic-agency", "name": "Dynamic Agency Suite", "category": "motion", "engine": "DynamicAgencySuite", "tags": ["dynamic", "agency", "professional"]},
    {"id": "vid-cinematic-fade", "name": "Cinematic Fade Suite", "category": "motion", "engine": "CinematicFadeSuite", "tags": ["cinematic", "fade", "smooth"]},
    {"id": "vid-kinetic-typo", "name": "Kinetic Typography Suite", "category": "typography", "engine": "KineticTypographySuite", "tags": ["kinetic", "typography", "text"]},
    {"id": "vid-mesh-abstract", "name": "Mesh Abstract Suite", "category": "abstract", "engine": "MeshAbstractSuite", "tags": ["mesh", "abstract", "modern"]},
    {"id": "vid-neon-circuit", "name": "Neon Circuit Suite", "category": "neon", "engine": "NeonCircuitSuite", "tags": ["neon", "circuit", "tech"]},
    {"id": "vid-product-showcase", "name": "Product Showcase Suite", "category": "product", "engine": "ProductShowcaseSuite", "tags": ["product", "showcase", "commercial"]},
    
    # New Video Templates (to be implemented)
    {"id": "vid-social-ad", "name": "Social Media Ad Suite", "category": "ads", "engine": "SocialMediaAdSuite", "tags": ["social", "ad", "tiktok", "reels"]},
    {"id": "vid-testimonial", "name": "Testimonial Suite", "category": "social-proof", "engine": "TestimonialSuite", "tags": ["testimonial", "review", "stars"]},
    {"id": "vid-product-launch", "name": "Product Launch Suite", "category": "launch", "engine": "ProductLaunchSuite", "tags": ["launch", "countdown", "features"]},
    {"id": "vid-comparison", "name": "Before/After Comparison Suite", "category": "comparison", "engine": "ComparisonSuite", "tags": ["comparison", "before-after", "split"]},
    {"id": "vid-data-viz", "name": "Data Visualization Suite", "category": "data", "engine": "DataVizSuite", "tags": ["data", "charts", "graphs"]},
    {"id": "vid-logo-anim", "name": "Logo Animation Suite", "category": "branding", "engine": "LogoAnimationSuite", "tags": ["logo", "animation", "brand"]},
    {"id": "vid-typography-bold", "name": "Bold Typography Suite", "category": "typography", "engine": "TypographySuite", "tags": ["bold", "typography", "kinetic"]},
    {"id": "vid-slideshow", "name": "Slideshow Maker Suite", "category": "slideshow", "engine": "SlideshowSuite", "tags": ["slideshow", "carousel", "photos"]},
    {"id": "vid-lower-thirds", "name": "Lower Thirds Suite", "category": "overlay", "engine": "LowerThirdsSuite", "tags": ["lower-thirds", "news", "overlay"]},
    {"id": "vid-end-screen", "name": "End Screen CTA Suite", "category": "cta", "engine": "EndScreenSuite", "tags": ["end-screen", "cta", "subscribe"]},
]


async def seed_templates():
    """Generate and insert template seed data."""
    logger.info("Starting template seed generation...")
    
    await init_db()
    session = await get_session_direct()
    
    try:
        # Create image templates
        logger.info(f"Creating {len(IMAGE_TEMPLATES)} image templates...")
        for tmpl in IMAGE_TEMPLATES:
            dimensions = json.dumps({"width": tmpl["width"], "height": tmpl["height"]})
            metadata = json.dumps({
                "tags": tmpl["tags"],
                "layout_seed": tmpl["layout_seed"],
                "theme": tmpl["theme"],
                "background_category": tmpl["theme"]
            })
            
            # Check if template already exists
            from sqlalchemy import select as sql_select
            result = await session.execute(
                sql_select(Template).where(Template.id == tmpl["id"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.info(f"Template {tmpl['id']} already exists, skipping...")
                continue
            
            new_template = Template(
                id=tmpl["id"],
                name=tmpl["name"],
                type="image",
                category=tmpl["category"],
                dimensions=dimensions,
                preview_url=f"/outputs/templates/{tmpl['id']}_preview.png",
                template_path=f"templates/{tmpl['id']}.json",
                metadata_json=metadata,
                usage_count=0
            )
            session.add(new_template)
        
        await session.commit()
        logger.success(f"✓ Created {len(IMAGE_TEMPLATES)} image templates")
        
        # Create video templates
        logger.info(f"Creating {len(VIDEO_TEMPLATES)} video templates...")
        for tmpl in VIDEO_TEMPLATES:
            metadata = json.dumps({
                "tags": tmpl["tags"],
                "engine": tmpl["engine"],
                "default_duration": 15,
                "aspect_ratios": ["9:16", "16:9", "1:1"]
            })
            
            # Check if template already exists
            from sqlalchemy import select as sql_select
            result = await session.execute(
                sql_select(Template).where(Template.id == tmpl["id"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.info(f"Template {tmpl['id']} already exists, skipping...")
                continue
            
            new_template = Template(
                id=tmpl["id"],
                name=tmpl["name"],
                type="video",
                category=tmpl["category"],
                dimensions=json.dumps({"width": 1080, "height": 1920}),
                preview_url=f"/outputs/templates/{tmpl['id']}_preview.mp4",
                template_path=f"templates/{tmpl['id']}.json",
                metadata_json=metadata,
                usage_count=0
            )
            session.add(new_template)
        
        await session.commit()
        logger.success(f"✓ Created {len(VIDEO_TEMPLATES)} video templates")
        
        logger.success("✨ Template seeding complete!")
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Error seeding templates: {e}")
        raise
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(seed_templates())
