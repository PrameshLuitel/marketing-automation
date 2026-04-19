"""
Add new video templates to the database.
Run with: python backend/scripts/add_video_templates.py
"""
import os
import sys
import json
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from storage.database import init_db, get_session_direct, Template
from loguru import logger


VIDEO_TEMPLATES = [
    # Countdown Promo
    {
        "id": "vid-countdown-001",
        "name": "Countdown Promotion",
        "type": "video",
        "category": "ads",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 9,
        "engine_id": "CountdownPromo",
        "description": "Animated countdown timer with brand colors, perfect for limited-time offers",
        "tags": ["countdown", "promotion", "sale", "urgent"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Quote Card
    {
        "id": "vid-quote-001",
        "name": "Quote Card",
        "type": "video",
        "category": "branding",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 9,
        "engine_id": "QuoteCard",
        "description": "Elegant quote display with gradient backgrounds and decorative elements",
        "tags": ["quote", "testimonial", "inspirational", "elegant"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Minimal Clean
    {
        "id": "vid-minimal-001",
        "name": "Minimal Clean",
        "type": "video",
        "category": "branding",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 9,
        "engine_id": "MinimalClean",
        "description": "Clean, minimal aesthetic with subtle animations and modern typography",
        "tags": ["minimal", "clean", "modern", "elegant"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Event Announcement
    {
        "id": "vid-event-001",
        "name": "Event Announcement",
        "type": "video",
        "category": "ads",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 9,
        "engine_id": "EventAnnouncement",
        "description": "Bold event announcement with animated gradients and pattern overlays",
        "tags": ["event", "announcement", "launch", "party"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Stats Counter
    {
        "id": "vid-stats-001",
        "name": "Stats Counter",
        "type": "video",
        "category": "motion",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 9,
        "engine_id": "StatsCounter",
        "description": "Animated statistics display with progress bars and glowing effects",
        "tags": ["statistics", "data", "numbers", "growth"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Before After
    {
        "id": "vid-beforeafter-001",
        "name": "Before & After",
        "type": "video",
        "category": "product",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 6,
        "engine_id": "BeforeAfter",
        "description": "Side-by-side comparison showing transformation or improvement",
        "tags": ["comparison", "transformation", "before-after", "results"],
        "scene_count": 2,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Social Media Ad (existing)
    {
        "id": "vid-social-001",
        "name": "Social Media Ad - Trending",
        "type": "video",
        "category": "ads",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 15,
        "engine_id": "SocialMediaAd",
        "description": "TikTok/Reels style ad with trending effects and engaging visuals",
        "tags": ["social", "ad", "trending", "viral"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Testimonial (existing)
    {
        "id": "vid-testimonial-001",
        "name": "Customer Testimonial",
        "type": "video",
        "category": "branding",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 15,
        "engine_id": "Testimonial",
        "description": "Customer review display with star ratings and professional styling",
        "tags": ["testimonial", "review", "customer", "stars"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Product Launch (existing)
    {
        "id": "vid-launch-001",
        "name": "Product Launch",
        "type": "video",
        "category": "product",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 15,
        "engine_id": "ProductLaunch",
        "description": "Countdown and feature highlights for new product launches",
        "tags": ["launch", "product", "features", "countdown"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Typography (existing)
    {
        "id": "vid-typo-001",
        "name": "Kinetic Typography",
        "type": "video",
        "category": "typography",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 10,
        "engine_id": "Typography",
        "description": "Bold kinetic text animations with dynamic movement",
        "tags": ["typography", "text", "kinetic", "bold"],
        "scene_count": 2,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Slideshow (existing)
    {
        "id": "vid-slideshow-001",
        "name": "Photo Slideshow",
        "type": "video",
        "category": "product",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 15,
        "engine_id": "Slideshow",
        "description": "Photo carousel with smooth transitions and text overlays",
        "tags": ["slideshow", "photos", "carousel", "gallery"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
    # Data Viz (existing)
    {
        "id": "vid-dataviz-001",
        "name": "Data Visualization",
        "type": "video",
        "category": "motion",
        "width": 1080,
        "height": 1920,
        "duration_seconds": 15,
        "engine_id": "DataViz",
        "description": "Animated charts and graphs with engaging data presentation",
        "tags": ["data", "charts", "visualization", "analytics"],
        "scene_count": 3,
        "output_format": "MP4 (H.264)",
        "fps": 30
    },
]


async def add_templates():
    """Add video templates to database."""
    logger.info("Initializing database...")
    await init_db()
    
    session = await get_session_direct()
    added_count = 0
    
    try:
        from sqlalchemy import select as sql_select
        
        for template_data in VIDEO_TEMPLATES:
            # Check if template already exists
            result = await session.execute(
                sql_select(Template).where(Template.id == template_data["id"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.info(f"Template {template_data['id']} already exists, skipping...")
                continue
            
            template = Template(
                id=template_data["id"],
                name=template_data["name"],
                type=template_data["type"],
                category=template_data["category"],
                dimensions=json.dumps({
                    "width": template_data["width"],
                    "height": template_data["height"]
                }),
                preview_url="",
                template_path="",
                metadata_json=json.dumps({
                    "engine_id": template_data["engine_id"],
                    "description": template_data["description"],
                    "tags": template_data["tags"],
                    "scene_count": template_data["scene_count"],
                    "duration_seconds": template_data["duration_seconds"],
                    "output_format": template_data["output_format"],
                    "fps": template_data["fps"]
                }),
                usage_count=0
            )
            
            session.add(template)
            added_count += 1
            logger.info(f"✓ Added template: {template_data['name']}")
        
        await session.commit()
        logger.info(f"\n✅ Successfully added {added_count} video templates!")
        
    except Exception as e:
        logger.error(f"Error adding templates: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(add_templates())
