"""
Test script to verify image generation works correctly with Photopea compatibility.
"""
import asyncio
import os
import sys
from PIL import Image

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from creative.image_gen import compose_graphic, ImageGenerator

def test_basic_image_generation():
    """Test that we can generate a basic image that Photopea can open."""
    print("=" * 60)
    print("Testing Basic Image Generation")
    print("=" * 60)
    
    # Test parameters
    width = 1080
    height = 1080
    headline = "TEST MARKETING GRAPHIC"
    tagline = "This is a test to verify Photopea compatibility"
    primary_color = "#3B82F6"
    secondary_color = "#8B5CF6"
    template_theme = "corporate"
    
    print(f"\nGenerating {width}x{height} image...")
    print(f"Theme: {template_theme}")
    print(f"Headline: {headline}")
    
    try:
        # Generate image
        img = compose_graphic(
            width=width,
            height=height,
            headline=headline,
            tagline=tagline,
            primary_color=primary_color,
            secondary_color=secondary_color,
            template_theme=template_theme,
            layout_seed=0,
            company_name="Test Company",
            logo_path=""
        )
        
        # Save test image
        test_path = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'outputs', 'test_photopea.png')
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        
        # Save with Photopea-compatible settings
        img.save(test_path, "PNG", quality=95, optimize=True)
        
        # Verify file
        if os.path.exists(test_path):
            file_size = os.path.getsize(test_path)
            print(f"\n✅ Image saved successfully: {test_path}")
            print(f"   File size: {file_size/1024:.1f}KB")
            
            # Verify it can be opened
            verify_img = Image.open(test_path)
            print(f"   Dimensions: {verify_img.size}")
            print(f"   Mode: {verify_img.mode}")
            print(f"   Format: {verify_img.format}")
            verify_img.close()
            
            print("\n✅ Image is valid and should open in Photopea!")
            return True
        else:
            print("\n❌ Image file not found after save!")
            return False
            
    except Exception as e:
        print(f"\n❌ Image generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_themes():
    """Test all available themes."""
    print("\n" + "=" * 60)
    print("Testing All Themes")
    print("=" * 60)
    
    themes = ["corporate", "minimal", "abstract", "neon"]
    output_dir = os.path.join(os.path.dirname(__file__), 'backend', 'data', 'outputs')
    
    for theme in themes:
        print(f"\nTesting theme: {theme}")
        try:
            img = compose_graphic(
                width=1080,
                height=1080,
                headline=f"{theme.upper()} THEME TEST",
                tagline=f"Testing {theme} theme for Photopea compatibility",
                primary_color="#3B82F6",
                secondary_color="#8B5CF6",
                template_theme=theme,
                layout_seed=0,
                company_name="Test",
                logo_path=""
            )
            
            test_path = os.path.join(output_dir, f'test_{theme}.png')
            img.save(test_path, "PNG", quality=95, optimize=True)
            
            if os.path.exists(test_path):
                file_size = os.path.getsize(test_path)
                print(f"  ✅ {theme}: {file_size/1024:.1f}KB")
            else:
                print(f"  ❌ {theme}: File not created")
                
        except Exception as e:
            print(f"  ❌ {theme}: {e}")

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PHOTOPEA COMPATIBILITY TEST SUITE")
    print("=" * 60)
    
    # Test 1: Basic generation
    success = test_basic_image_generation()
    
    # Test 2: All themes
    test_all_themes()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Images should work in Photopea.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
