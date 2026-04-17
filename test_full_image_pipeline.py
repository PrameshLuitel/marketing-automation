"""
Test script to verify image generation and database storage works end-to-end.
This script:
1. Generates test images using the ImageGenerator
2. Adds them to the database as CreativeAsset entries
3. Verifies they can be retrieved via the gallery query
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from creative.image_gen import ImageGenerator
from storage.database import get_session_direct, CreativeAsset, Campaign
from sqlalchemy import select


async def test_image_generation_and_storage():
    print("=" * 70)
    print("TESTING: Image Generation & Database Storage")
    print("=" * 70)
    
    # Step 1: Generate images
    print("\n[Step 1] Generating test images...")
    profile = {
        "company_name": "Himalayan Haulers",
        "brand_primary_color": "#2563EB",
        "brand_secondary_color": "#7C3AED",
        "logo_url": ""  # No logo for this test
    }
    
    config = {
        "graphics_config": {
            "headline": "Move Smarter, Ship Faster",
            "tagline": "Nepal's first digital trucking platform connecting shippers with carriers.",
            "template_theme": "abstract",
            "layout_seed": 42,
        },
        "graphic_size": "both"  # Generate both square and portrait
    }
    
    gen = ImageGenerator({"company": profile}, run_id="test_integration")
    result = await gen.generate_async(config)
    
    print(f"\n✅ Image generation result:")
    print(f"   Type: {result['type']}")
    print(f"   Images generated: {len(result['image_urls'])}")
    for url in result['image_urls']:
        print(f"   - {url}")
    
    # Step 2: Add to database
    print("\n[Step 2] Adding images to database...")
    session = await get_session_direct()
    
    # Get first campaign to link to
    campaign_result = await session.execute(select(Campaign).limit(1))
    campaign = campaign_result.scalar_one_or_none()
    
    if campaign:
        print(f"   Linking to campaign ID: {campaign.id}")
        campaign_id = campaign.id
    else:
        print("   ⚠️  No campaigns found, creating without campaign link")
        campaign_id = None
    
    # Create CreativeAsset entries for each generated image
    added_assets = []
    for image_url in result['image_urls']:
        # Determine if it's square or portrait from the URL
        is_square = 'sq' in image_url
        size_label = 'Square' if is_square else 'Portrait'
        
        asset = CreativeAsset(
            campaign_id=campaign_id,
            asset_type='image',
            file_path=image_url,
            prompt=f"{size_label} Marketing Design - Move Smarter, Ship Faster"
        )
        session.add(asset)
        added_assets.append(image_url)
        print(f"   ✓ Added: {image_url}")
    
    await session.commit()
    print(f"\n✅ Successfully added {len(added_assets)} images to database!")
    
    # Step 3: Verify retrieval
    print("\n[Step 3] Verifying images can be retrieved...")
    result = await session.execute(
        select(CreativeAsset)
        .where(CreativeAsset.asset_type == 'image')
        .order_by(CreativeAsset.created_at.desc())
    )
    images = result.scalars().all()
    
    print(f"\n✅ Total image assets in database: {len(images)}")
    for img in images:
        print(f"   ID: {img.id:2d} | Type: {img.asset_type:5s} | Path: {img.file_path}")
    
    # Step 4: Verify files exist on disk
    print("\n[Step 4] Verifying image files exist on disk...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    for img in images:
        # Convert /outputs/... to actual path
        relative_path = img.file_path.replace('/outputs/', '')
        full_path = os.path.join(backend_dir, 'data', 'outputs', relative_path)
        
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"   ✓ {img.file_path} ({file_size/1024:.1f}KB)")
        else:
            print(f"   ✗ {img.file_path} - FILE NOT FOUND!")
    
    await session.close()
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)
    print(f"\nSummary:")
    print(f"  - Images generated: {len(result['image_urls'])}")
    print(f"  - Images saved to DB: {len(added_assets)}")
    print(f"  - Total images in DB: {len(images)}")
    print(f"\nYou should now see {len(images)} designs in the Image Studio gallery!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_image_generation_and_storage())
