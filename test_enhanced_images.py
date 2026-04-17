"""
Test the enhanced image generator with 50+ templates and company assets
Generates 10 professional marketing design variations
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from creative.image_gen_enhanced import ImageGenerator, LAYOUTS
from storage.database import get_session_direct, CreativeAsset, Campaign
from sqlalchemy import select

async def test_enhanced_generation():
    print("=" * 80)
    print("ENHANCED IMAGE GENERATOR TEST - 50+ Professional Templates")
    print("=" * 80)
    
    # Show available templates
    print(f"\n📊 Available Layout Templates: {len(LAYOUTS)}")
    print("\nTemplate Categories:")
    categories = {}
    for layout in LAYOUTS:
        style = layout.get('id', '').split('-')[0]
        if style not in categories:
            categories[style] = []
        categories[style].append(layout['id'])
    
    for cat, layouts in categories.items():
        print(f"  • {cat.upper()}: {len(layouts)} templates")
        for layout in layouts[:3]:
            print(f"    - {layout}")
        if len(layouts) > 3:
            print(f"    ... and {len(layouts) - 3} more")
    
    # Company profile with assets
    profile = {
        "company_name": "Himalayan Haulers",
        "brand_primary_color": "#2563EB",
        "brand_secondary_color": "#7C3AED",
        "logo_url": "http://localhost:5175/outputs/assets/asset_9205f4f4.png",
        "product_images": [
            "http://localhost:5175/outputs/assets/asset_b3057b3a.png",
            "http://localhost:5175/outputs/assets/asset_19f0fceb.png",
            "http://localhost:5175/outputs/assets/asset_481ea853.png",
        ]
    }
    
    config = {
        "graphics_config": {
            "headline": "Move Smarter, Ship Faster",
            "tagline": "Nepal's first digital trucking platform connecting shippers with carriers.",
            "template_theme": "abstract",
            "layout_seed": 42,
        },
        "graphic_size": "both",  # square + portrait
        "num_variations": 10  # Generate 10 different designs
    }
    
    print(f"\n🎨 Generating 10 design variations...")
    print(f"   Company: {profile['company_name']}")
    print(f"   Logo: {'✓' if profile['logo_url'] else '✗'}")
    print(f"   Product Images: {len(profile['product_images'])}")
    
    # Generate images
    gen = ImageGenerator({"company": profile}, run_id="enhanced_test")
    result = await gen.generate_async(config)
    
    print(f"\n✅ Generation Complete!")
    print(f"   Total designs created: {len(result['image_urls'])}")
    for i, url in enumerate(result['image_urls'], 1):
        full_path = os.path.join(os.path.dirname(__file__), 'backend', url.lstrip('/'))
        if os.path.exists(full_path):
            size = os.path.getsize(full_path) / 1024
            print(f"   {i:2d}. {url} ({size:.1f}KB)")
    
    # Add to database
    print(f"\n💾 Saving to database...")
    session = await get_session_direct()
    
    # Get first campaign
    campaign_result = await session.execute(select(Campaign).limit(1))
    campaign = campaign_result.scalar_one_or_none()
    campaign_id = campaign.id if campaign else None
    
    # Create asset entries
    for image_url in result['image_urls']:
        asset = CreativeAsset(
            campaign_id=campaign_id,
            asset_type='image',
            file_path=image_url,
            prompt=f"Professional Marketing Design - {profile['company_name']}"
        )
        session.add(asset)
    
    await session.commit()
    
    # Verify
    result = await session.execute(select(CreativeAsset).where(CreativeAsset.asset_type == 'image'))
    images = result.scalars().all()
    print(f"✅ Total image assets in database: {len(images)}")
    
    await session.close()
    
    print("\n" + "=" * 80)
    print("SUCCESS! You should now see multiple designs in the Image Studio gallery!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_enhanced_generation())
