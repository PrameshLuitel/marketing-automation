"""
Generate multiple layered designs with different themes and layouts
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import random
from PIL import Image
from creative.image_gen_enhanced import compose_graphic_layered, LAYOUTS


def generate_multiple_designs():
    """Generate 5 different layered designs with variety"""
    
    print("=" * 70)
    print("GENERATING 5 DIFFERENT LAYERED DESIGNS")
    print("=" * 70)
    
    # Company assets
    logo_path = "/Users/prameshluitel/Documents/Marketing Deparment Automation/backend/data/outputs/assets/asset_9205f4f4.png"
    product_images = [
        "/Users/prameshluitel/Documents/Marketing Deparment Automation/backend/data/outputs/assets/asset_b3057b3a.png"
    ]
    
    # Design configurations - 5 different styles
    designs = [
        {
            "name": "corporate_hero",
            "theme": "corporate",
            "layout_seed": 2,
            "headline": "TRANSFORM YOUR BUSINESS",
            "tagline": "Digital solutions for the modern enterprise",
            "primary": "#1E40AF",
            "secondary": "#3B82F6",
        },
        {
            "name": "minimal_elegant",
            "theme": "minimal",
            "layout_seed": 12,
            "headline": "LESS IS MORE",
            "tagline": "Simplicity is the ultimate sophistication",
            "primary": "#1F2937",
            "secondary": "#6B7280",
        },
        {
            "name": "abstract_creative",
            "theme": "abstract",
            "layout_seed": 25,
            "headline": "CREATE WITHOUT LIMITS",
            "tagline": "Where innovation meets imagination",
            "primary": "#7C3AED",
            "secondary": "#EC4899",
        },
        {
            "name": "neon_bold",
            "theme": "neon",
            "layout_seed": 35,
            "headline": "FUTURE IS NOW",
            "tagline": "Next-generation technology solutions",
            "primary": "#06B6D4",
            "secondary": "#8B5CF6",
        },
        {
            "name": "luxury_premium",
            "theme": "luxury",
            "layout_seed": 45,
            "headline": "EXCELLENCE DELIVERED",
            "tagline": "Premium quality, exceptional results",
            "primary": "#B45309",
            "secondary": "#F59E0B",
        },
    ]
    
    output_dir = "/Users/prameshluitel/Documents/Marketing Deparment Automation/data/outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    all_results = []
    
    for idx, design_cfg in enumerate(designs, 1):
        print(f"\n{'='*70}")
        print(f"DESIGN {idx}/5: {design_cfg['name'].upper()}")
        print(f"{'='*70}")
        
        width, height = 1080, 1080
        
        print(f"🎨 Theme: {design_cfg['theme']}")
        print(f"📝 Headline: {design_cfg['headline']}")
        print(f"📐 Layout: {LAYOUTS[design_cfg['layout_seed']]['id']}")
        
        # Generate layered design
        result = compose_graphic_layered(
            width, height,
            design_cfg['headline'],
            design_cfg['tagline'],
            design_cfg['primary'],
            design_cfg['secondary'],
            design_cfg['theme'],
            design_cfg['layout_seed'],
            "Himalayan Haulers",
            logo_path,
            product_images
        )
        
        # Save layers
        base_filename = os.path.join(output_dir, f"design_{design_cfg['name']}")
        
        print(f"\n💾 Saving layers...")
        
        # Create composite
        composite = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        for layer_name in ['background', 'products', 'gradient_overlay', 'text', 'logo']:
            if layer_name in result['layers']:
                composite = Image.alpha_composite(composite, result['layers'][layer_name])
        
        # Save individual layers
        layer_count = 0
        for layer_name, layer_img in result['layers'].items():
            if layer_img.mode != 'RGBA':
                layer_img = layer_img.convert('RGBA')
            
            layer_filename = f"{base_filename}_{layer_name}.png"
            layer_img.save(layer_filename, 'PNG')
            layer_count += 1
        
        # Save preview
        preview_path = f"{base_filename}_preview.png"
        composite.save(preview_path, 'PNG', quality=95, optimize=True)
        
        preview_size = os.path.getsize(preview_path) / 1024
        print(f"  ✓ Preview: {preview_size:.1f}KB")
        print(f"  ✓ {layer_count} layers saved")
        
        all_results.append({
            'name': design_cfg['name'],
            'theme': design_cfg['theme'],
            'preview': preview_path,
            'layers': layer_count
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ ALL 5 DESIGNS GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📁 Location: {output_dir}")
    print(f"\n🎨 DESIGNS CREATED:")
    
    for idx, res in enumerate(all_results, 1):
        print(f"\n{idx}. {res['name'].upper()} ({res['theme']} theme)")
        print(f"   Preview: {os.path.basename(res['preview'])}")
        print(f"   Layers: {res['layers']} individual PNG files")
    
    print(f"\n🎯 HOW TO EDIT:")
    print(f"   1. Go to https://www.photopea.com")
    print(f"   2. Open any preview PNG")
    print(f"   3. Drag & drop the layer files")
    print(f"   4. Edit each layer independently!")
    print("=" * 70)


if __name__ == "__main__":
    generate_multiple_designs()
