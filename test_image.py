import asyncio
import sys
sys.path.insert(0, "backend")
from creative.image_gen import ImageGenerator

async def main():
    profile = {
        "company_name": "Himalayan Haulers",
        "brand_primary_color": "#2563EB",
        "brand_secondary_color": "#7C3AED",
    }
    config = {
        "graphics_config": {
            "headline": "Move Smarter, Ship Faster",
            "tagline": "Nepal's first digital trucking platform connecting shippers with carriers.",
            "template_theme": "abstract",
            "layout_seed": 3,
        },
        "graphic_size": "both"
    }
    gen = ImageGenerator({"company": profile}, run_id="test_pillow")
    res = await gen.generate_async(config)
    print("RESULT:", res)

asyncio.run(main())
