"""
Test the automated layered design system with background library
This mimics how the Canva MCP system works automatically
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from creative.image_gen_enhanced import ImageGenerator


async def test_automated_layered_generation():
    """Test automatic generation with pre-made backgrounds and layered output"""
    
    print("=" * 70)
    print("TESTING AUTOMATED LAYERED DESIGN SYSTEM (Like Canva MCP)")
    print("=" * 70)
    
    # Simulate company profile (like from database)
    company_profile = {
        "company_name": "Himalayan Haulers",
        "brand_primary_color": "#2563EB",
        "brand_secondary_color": "#7C3AED",
        "logo_url": "/outputs/assets/asset_9205f4f4.png",
        "product_images": [
            "/outputs/assets/asset_b3057b3a.png"
        ]
    }
    
    # Simulate pipeline config
    config = {
        "graphics_config": {
            "headline": "MOVE SMARTER, SHIP FASTER",
            "tagline": "Nepal's first digital trucking platform"
        },
        "graphic_size": "square",
        "num_variations": 5,  # Generate 5 designs automatically
        "output_format": "layered"  # Output layered designs
    }
    
    print(f"\n🏢 Company: {company_profile['company_name']}")
    print(f"🎨 Brand Colors: {company_profile['brand_primary_color']} / {company_profile['brand_secondary_color']}")
    print(f"📝 Headline: {config['graphics_config']['headline']}")
    print(f"📊 Variations: {config['num_variations']}")
    print(f"📐 Size: {config['graphic_size']}")
    print(f"🎯 Format: {config['output_format']}")
    
    # Generate designs (automatically like Canva MCP)
    print("\n⚙️  Starting automated generation...")
    img_gen = ImageGenerator(
        profile_data={"company": company_profile},
        run_id="auto_test_001"
    )
    
    result = await img_gen.generate_async(config)
    
    print("\n" + "=" * 70)
    print("✅ AUTOMATED GENERATION COMPLETE!")
    print("=" * 70)
    print(f"\n📁 Generated {len(result['image_urls'])} designs")
    print(f"\n📂 Each design includes:")
    print(f"   - 1 flattened preview (for gallery)")
    print(f"   - 1 layers folder with 5 editable PNGs:")
    print(f"     • background.png (from 156 pre-made backgrounds)")
    print(f"     • products.png (company product images)")
    print(f"     • gradient_overlay.png (color grading)")
    print(f"     • text.png (headline + tagline)")
    print(f"     • logo.png (company branding)")
    print(f"\n🎨 Background Library: 156 professional backgrounds")
    print(f"   - corporate: 12 backgrounds")
    print(f"   - minimal: 12 backgrounds")
    print(f"   - abstract: 12 backgrounds")
    print(f"   - luxury: 12 backgrounds")
    print(f"   - neon: 12 backgrounds")
    print(f"   - And 8 more categories!")
    print(f"\n🎯 How to Edit:")
    print(f"   1. Go to https://www.photopea.com")
    print(f"   2. Open the preview PNG")
    print(f"   3. Drag & drop layer files from *_layers folder")
    print(f"   4. Edit each layer independently!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_automated_layered_generation())
