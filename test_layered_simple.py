"""
Generate layered designs with individual PNG layers for easy Photopea editing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from PIL import Image
from creative.image_gen_enhanced import compose_graphic_layered


def save_layered_design(layers_dict: dict, output_base_path: str):
    """
    Save layered design as individual PNG files.
    This is the most compatible approach for Photopea.
    """
    
    # Get dimensions
    first_layer = next(iter(layers_dict.values()))
    width, height = first_layer.size
    
    print(f"📐 Canvas: {width}x{height}")
    print(f"📑 Layers: {len(layers_dict)}")
    
    # Create composite for preview
    composite = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    for layer_name in ['background', 'products', 'gradient_overlay', 'text', 'logo']:
        if layer_name in layers_dict:
            composite = Image.alpha_composite(composite, layers_dict[layer_name])
    
    # Save individual layers
    layer_files = []
    for layer_name, layer_img in layers_dict.items():
        if layer_img.mode != 'RGBA':
            layer_img = layer_img.convert('RGBA')
        
        layer_filename = f"{output_base_path}_{layer_name}.png"
        layer_img.save(layer_filename, 'PNG')
        
        file_size = os.path.getsize(layer_filename) / 1024
        layer_files.append((layer_name, file_size))
        print(f"  ✓ {layer_name}: {file_size:.1f}KB")
    
    # Save flattened preview
    preview_path = f"{output_base_path}_preview.png"
    composite.save(preview_path, 'PNG', quality=95, optimize=True)
    
    print(f"\n💾 Saved {len(layer_files)} layers + preview")
    return {
        'preview': preview_path,
        'layers': layer_files
    }


def generate_layered_demo():
    """Generate a demo with proper layers for Photopea"""
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
    output_dir = os.path.join(os.path.dirname(__file__), 'data', 'outputs')
    os.makedirs(output_dir, exist_ok=True)
    
    base_filename = os.path.join(output_dir, "design_layered_demo")
    
    print(f"\n💾 Saving layers...")
    info = save_layered_design(result['layers'], base_filename)
    
    print("\n" + "=" * 70)
    print("✅ LAYERS GENERATED SUCCESSFULLY!")
    print("=" * 70)
    print(f"\n📁 Files created in: {output_dir}")
    print(f"\n🎨 HOW TO EDIT IN PHOTOPEA:")
    print(f"   1. Go to https://www.photopea.com")
    print(f"   2. File → Open → Select: design_layered_demo_preview.png")
    print(f"   3. File → Open & Place → Select each layer PNG")
    print(f"   4. Each layer is now editable!")
    print(f"\n📦 Layer structure (bottom to top):")
    for idx, (name, size) in enumerate(info['layers']):
        print(f"   {idx+1}. {name.capitalize()} ({size:.1f}KB)")
    print("=" * 70)


if __name__ == "__main__":
    generate_layered_demo()
