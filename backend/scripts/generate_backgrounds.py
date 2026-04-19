"""
Generate diverse background templates for the design studio.
Creates 200+ backgrounds across all themes using the existing gradient background generator.

Run with: python backend/scripts/generate_backgrounds.py
"""
import os
import sys
import random

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from creative.image_gen_enhanced import _generate_gradient_background, LAYOUTS
from loguru import logger
from pathlib import Path


# ── Background Generation Configuration ───────────────────

THEMES = ['corporate', 'minimal', 'abstract', 'neon', 'luxury']

COLOR_PALETTES = {
    'corporate': [
        ('#1B3A5C', '#2C5F8A'),  # Navy blue
        ('#0F2B45', '#1E4961'),  # Dark navy
        ('#2C3E50', '#34495E'),  # Slate gray
        ('#1A252F', '#2C3E50'),  # Charcoal
        ('#0D2538', '#1B3A5C'),  # Deep ocean
    ],
    'minimal': [
        ('#F5F5F5', '#E8E8E8'),  # Light gray
        ('#FFFFFF', '#F0F0F0'),  # Pure white
        ('#FAFAFA', '#F5F5F5'),  # Off-white
        ('#E8E8E8', '#D8D8D8'),  # Silver
        ('#F8F8F8', '#ECECEC'),  # Platinum
    ],
    'abstract': [
        ('#667eea', '#764ba2'),  # Purple gradient
        ('#f093fb', '#f5576c'),  # Pink to red
        ('#4facfe', '#00f2fe'),  # Cyan blue
        ('#43e97b', '#38f9d7'),  # Green mint
        ('#fa709a', '#fee140'),  # Pink yellow
        ('#a8edea', '#fed6e3'),  # Pastel
        ('#ff9a9e', '#fecfef'),  # Rose
        ('#ffecd2', '#fcb69f'),  # Peach
    ],
    'neon': [
        ('#00f2fe', '#4facfe'),  # Cyan
        ('#00ff87', '#60efff'),  # Green cyan
        ('#ff00ff', '#00ffff'),  # Magenta cyan
        ('#ff0080', '#7928ca'),  # Pink purple
        ('#00ff00', '#0080ff'),  # Green blue
        ('#ff0040', '#ff00ff'),  # Red magenta
    ],
    'luxury': [
        ('#FFD700', '#FFA500'),  # Gold
        ('#C0C0C0', '#808080'),  # Silver
        ('#B76E79', '#D4A574'),  # Rose gold
        ('#1C1C1C', '#2C2C2C'),  # Black premium
        ('#8B4513', '#D2691E'),  # Bronze
        ('#2F4F4F', '#708090'),  # Slate luxury
    ],
}


def generate_backgrounds(output_dir, count_per_theme=40):
    """Generate diverse backgrounds for each theme."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    total_generated = 0
    
    for theme in THEMES:
        logger.info(f"Generating {count_per_theme} {theme} backgrounds...")
        palettes = COLOR_PALETTES[theme]
        
        for i in range(count_per_theme):
            # Random dimensions (common marketing sizes)
            sizes = [
                (1080, 1080),   # Instagram square
                (1080, 1350),   # Instagram portrait
                (1080, 1920),   # Story
                (1200, 675),    # Twitter
                (1200, 627),    # LinkedIn
                (1280, 720),    # YouTube
            ]
            width, height = random.choice(sizes)
            
            # Random color palette
            primary, secondary = random.choice(palettes)
            
            # Generate background
            try:
                bg_image = _generate_gradient_background(width, height, primary, secondary, theme)
                
                # Save with descriptive name
                filename = f"bg_{theme}_{width}x{height}_v{i+1}.png"
                filepath = os.path.join(output_dir, filename)
                
                bg_image.save(filepath, "PNG", quality=95, optimize=True)
                
                file_size = os.path.getsize(filepath) / 1024
                logger.debug(f"  ✓ {filename} ({file_size:.1f}KB)")
                total_generated += 1
                
            except Exception as e:
                logger.error(f"  ✗ Failed to generate {theme} background {i+1}: {e}")
        
        logger.success(f"✓ Generated {count_per_theme} {theme} backgrounds")
    
    return total_generated


def main():
    """Main execution."""
    logger.info("🎨 Background Template Generator")
    logger.info("=" * 50)
    
    # Output directory
    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'creative', 'data', 'outputs', 'backgrounds'
    )
    
    logger.info(f"Output directory: {output_dir}")
    
    # Count existing backgrounds
    if os.path.exists(output_dir):
        existing = len([f for f in os.listdir(output_dir) if f.endswith('.png')])
        logger.info(f"Existing backgrounds: {existing}")
    
    # Generate new backgrounds
    count_per_theme = 40  # 40 per theme × 5 themes = 200 total
    generated = generate_backgrounds(output_dir, count_per_theme)
    
    logger.info("=" * 50)
    logger.success(f"✨ Generated {generated} new backgrounds!")
    logger.success(f"📁 Saved to: {output_dir}")
    
    # Summary
    total = len([f for f in os.listdir(output_dir) if f.endswith('.png')])
    logger.info(f"Total backgrounds in library: {total}")


if __name__ == "__main__":
    main()
