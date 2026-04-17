"""
Generate layered designs with individual PNG layers for Photopea editing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from creative.image_gen_enhanced import compose_graphic_layered
from PIL import Image

async def generate_layered_design():
    print("=" * 70)
    print("GENERATING LAYERED DESIGN FOR PHOTOPEA")
    print("=" * 70)
    
    # Design parameters
    width, height = 1080, 1080
    headline = "MOVE SMARTER, SHIP FASTER"
    tagline = "Nepal's first digital trucking platform"
    primary = "#2563EB"
    secondary = "#7C3AED"
    theme = "abstract"
    layout_seed = 15
    company_name = "Himalayan Haulers"
    logo_path = "/Users/prameshluitel/Documents/Marketing Deparment Automation/backend/data/outputs/assets/asset_9205f4f4.png"
    product_images = [
        "/Users/prameshluitel/Documents/Marketing Deparment Automation/backend/data/outputs/assets/asset_b3057b3a.png"
    ]
    
    print(f"\n📐 Size: {width}x{height}")
    print(f"🎨 Theme: {theme}")
    print(f"📝 Headline: {headline}")
    print(f"🏢 Company: {company_name}")
    print(f"🖼️  Logo: {'✓' if os.path.exists(logo_path) else '✗'}")
    print(f"📦 Products: {len(product_images)}")
    
    # Generate layered design
    print("\n⚙️  Generating layered design...")
    result = compose_graphic_layered(
        width, height, headline, tagline, primary, secondary,
        theme, layout_seed, company_name, logo_path, product_images
    )
    
    # Save layers
    output_dir = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'outputs')
    run_id = "layered_demo"
    variation = 1
    
    print(f"\n💾 Saving layers...")
    
    # Save flattened composite
    composite_path = os.path.join(output_dir, f"design_sq_{run_id}_v{variation}.png")
    result['composite'].save(composite_path, "PNG", quality=95, optimize=True)
    print(f"  ✓ Composite: design_sq_{run_id}_v{variation}.png")
    
    # Save individual layers
    for layer_name, layer_img in result['layers'].items():
        layer_path = os.path.join(output_dir, f"design_sq_{run_id}_v{variation}_{layer_name}.png")
        layer_img.save(layer_path, "PNG")
        layer_size = os.path.getsize(layer_path) / 1024
        print(f"  ✓ Layer '{layer_name}': {layer_size:.1f}KB")
    
    print("\n" + "=" * 70)
    print("LAYERS GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📁 Files created in: {output_dir}")
    print(f"\n🎨 To edit in Photopea:")
    print(f"   1. Go to https://www.photopea.com")
    print(f"   2. Open the composite PNG")
    print(f"   3. File → Open & Place each layer PNG")
    print(f"   4. Edit layers independently!")
    print(f"\n📦 Layer structure:")
    print(f"   1. Background - Gradient/pattern base")
    print(f"   2. Products - Product images with shadows")
    print(f"   3. Gradient Overlay - Color grading")
    print(f"   4. Text - Headline, tagline, company name")
    print(f"   5. Logo - Company branding")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(generate_layered_design())
