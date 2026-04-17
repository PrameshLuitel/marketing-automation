"""
Generate a library of 100+ professional background templates
These are pre-made backgrounds that can be used for marketing designs
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PIL import Image, ImageDraw, ImageFilter
import random
import math


def generate_gradient_background(width, height, style, colors):
    """Generate gradient background"""
    img = Image.new('RGB', (width, height), colors[0])
    draw = ImageDraw.Draw(img)
    
    if style == 'vertical':
        for y in range(height):
            ratio = y / height
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    elif style == 'horizontal':
        for x in range(width):
            ratio = x / width
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    elif style == 'diagonal':
        for y in range(height):
            for x in range(width):
                ratio = (x + y) / (width + height)
                r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
                g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
                b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
                draw.point((x, y), fill=(r, g, b))
    elif style == 'radial':
        cx, cy = width // 2, height // 2
        max_dist = math.sqrt(cx**2 + cy**2)
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                ratio = min(dist / max_dist, 1.0)
                r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * ratio)
                g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * ratio)
                b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * ratio)
                draw.point((x, y), fill=(r, g, b))
    
    return img


def generate_geometric_background(width, height, style, colors):
    """Generate geometric pattern background"""
    img = Image.new('RGB', (width, height), colors[0])
    draw = ImageDraw.Draw(img)
    
    if style == 'circles':
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(50, 200)
            color = random.choice(colors)
            alpha = random.randint(30, 100)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                        fill=(*color, alpha) if len(color) == 3 else color)
    elif style == 'triangles':
        for _ in range(15):
            points = [
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height)),
                (random.randint(0, width), random.randint(0, height))
            ]
            color = random.choice(colors)
            draw.polygon(points, fill=color)
    elif style == 'grid':
        spacing = random.randint(40, 80)
        for x in range(0, width, spacing):
            draw.line([(x, 0), (x, height)], fill=colors[1], width=1)
        for y in range(0, height, spacing):
            draw.line([(0, y), (width, y)], fill=colors[1], width=1)
    elif style == 'dots':
        spacing = random.randint(20, 40)
        for x in range(0, width, spacing):
            for y in range(0, height, spacing):
                radius = random.randint(2, 5)
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=colors[1])
    
    return img


def generate_abstract_background(width, height, style, colors):
    """Generate abstract artistic background"""
    img = Image.new('RGB', (width, height), colors[0])
    draw = ImageDraw.Draw(img)
    
    if style == 'waves':
        for y in range(0, height, 5):
            points = []
            for x in range(0, width, 10):
                wave_y = y + math.sin(x * 0.02) * 20
                points.append((x, wave_y))
            color = random.choice(colors)
            for i in range(len(points) - 1):
                draw.line([points[i], points[i+1]], fill=color, width=3)
    elif style == 'noise':
        import numpy as np
        noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
        noise_img = Image.fromarray(noise, 'RGB')
        base = Image.new('RGB', (width, height), colors[0])
        img = Image.blend(base, noise_img, 0.3)
        return img
    elif style == 'blur_orbs':
        for _ in range(10):
            orb = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            orb_draw = ImageDraw.Draw(orb)
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(100, 300)
            color = random.choice(colors)
            orb_draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=(*color, 80))
            orb = orb.filter(ImageFilter.GaussianBlur(radius=50))
            img = Image.alpha_composite(img.convert('RGBA'), orb).convert('RGB')
    elif style == 'mesh':
        for _ in range(30):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            color = random.choice(colors)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(1, 3))
    
    return img


def generate_texture_background(width, height, style, colors):
    """Generate textured background"""
    img = Image.new('RGB', (width, height), colors[0])
    
    if style == 'paper':
        import numpy as np
        noise = np.random.randint(240, 255, (height, width, 3), dtype=np.uint8)
        img = Image.fromarray(noise, 'RGB')
    elif style == 'fabric':
        draw = ImageDraw.Draw(img)
        for y in range(0, height, 4):
            draw.line([(0, y), (width, y)], fill=(colors[0][0]+10, colors[0][1]+10, colors[0][2]+10), width=1)
    elif style == 'concrete':
        import numpy as np
        noise = np.random.randint(180, 220, (height, width, 3), dtype=np.uint8)
        img = Image.fromarray(noise, 'RGB')
        img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    return img


# Color palettes (100+ combinations)
COLOR_PALETTES = [
    # Corporate Blues
    {'name': 'ocean_deep', 'colors': [(30, 64, 175), (59, 130, 246)], 'category': 'corporate'},
    {'name': 'sky_light', 'colors': [(147, 197, 253), (219, 234, 254)], 'category': 'corporate'},
    {'name': 'navy_pro', 'colors': [(30, 58, 138), (100, 116, 139)], 'category': 'corporate'},
    {'name': 'business_blue', 'colors': [(37, 99, 235), (147, 197, 253)], 'category': 'corporate'},
    
    # Modern Grays
    {'name': 'slate_elegant', 'colors': [(51, 65, 85), (148, 163, 184)], 'category': 'minimal'},
    {'name': 'silver_clean', 'colors': [(209, 213, 219), (243, 244, 246)], 'category': 'minimal'},
    {'name': 'charcoal_dark', 'colors': [(31, 41, 55), (75, 85, 99)], 'category': 'minimal'},
    {'name': 'platinum', 'colors': [(229, 231, 235), (255, 255, 255)], 'category': 'minimal'},
    
    # Vibrant Gradients
    {'name': 'purple_pink', 'colors': [(124, 58, 237), (236, 72, 153)], 'category': 'abstract'},
    {'name': 'sunset', 'colors': [(251, 146, 60), (244, 63, 94)], 'category': 'abstract'},
    {'name': 'aurora', 'colors': [(6, 182, 212), (139, 92, 246)], 'category': 'abstract'},
    {'name': 'neon_vibe', 'colors': [(16, 185, 129), (59, 130, 246)], 'category': 'abstract'},
    
    # Luxury Golds
    {'name': 'gold_premium', 'colors': [(180, 83, 9), (245, 158, 11)], 'category': 'luxury'},
    {'name': 'champagne', 'colors': [(251, 191, 36), (253, 230, 138)], 'category': 'luxury'},
    {'name': 'bronze_elegant', 'colors': [(120, 53, 15), (217, 119, 6)], 'category': 'luxury'},
    {'name': 'royal_gold', 'colors': [(161, 98, 7), (251, 146, 60)], 'category': 'luxury'},
    
    # Nature Greens
    {'name': 'forest', 'colors': [(21, 128, 61), (74, 222, 128)], 'category': 'nature'},
    {'name': 'emerald', 'colors': [(4, 120, 87), (110, 231, 183)], 'category': 'nature'},
    {'name': 'lime_fresh', 'colors': [(63, 98, 18), (132, 204, 22)], 'category': 'nature'},
    {'name': 'mint_clean', 'colors': [(100, 116, 139), (209, 213, 219)], 'category': 'nature'},
    
    # Warm Tones
    {'name': 'coral_warm', 'colors': [(251, 113, 133), (253, 186, 116)], 'category': 'warm'},
    {'name': 'terracotta', 'colors': [(194, 65, 12), (251, 146, 60)], 'category': 'warm'},
    {'name': 'peach_soft', 'colors': [(251, 207, 232), (254, 215, 170)], 'category': 'warm'},
    {'name': 'amber_glow', 'colors': [(245, 158, 11), (252, 211, 77)], 'category': 'warm'},
    
    # Bold Reds
    {'name': 'crimson', 'colors': [(185, 28, 28), (248, 113, 113)], 'category': 'bold'},
    {'name': 'ruby', 'colors': [(159, 18, 57), (244, 63, 94)], 'category': 'bold'},
    {'name': 'fire', 'colors': [(220, 38, 38), (251, 146, 60)], 'category': 'bold'},
    {'name': 'cherry', 'colors': [(190, 18, 60), (236, 72, 153)], 'category': 'bold'},
    
    # Cool Purples
    {'name': 'violet', 'colors': [(91, 33, 182), (167, 139, 250)], 'category': 'cool'},
    {'name': 'lavender', 'colors': [(139, 92, 246), (221, 214, 254)], 'category': 'cool'},
    {'name': 'plum', 'colors': [(107, 33, 168), (192, 132, 252)], 'category': 'cool'},
    {'name': 'orchid', 'colors': [(124, 58, 237), (216, 180, 254)], 'category': 'cool'},
    
    # Dark Themes
    {'name': 'midnight', 'colors': [(15, 23, 42), (51, 65, 85)], 'category': 'dark'},
    {'name': 'obsidian', 'colors': [(3, 7, 18), (30, 41, 59)], 'category': 'dark'},
    {'name': 'carbon', 'colors': [(23, 23, 23), (82, 82, 82)], 'category': 'dark'},
    {'name': 'noir', 'colors': [(10, 10, 10), (50, 50, 50)], 'category': 'dark'},
    
    # Pastel Soft
    {'name': 'baby_blue', 'colors': [(186, 230, 253), (224, 242, 254)], 'category': 'pastel'},
    {'name': 'pink_candy', 'colors': [(252, 165, 165), (254, 205, 211)], 'category': 'pastel'},
    {'name': 'mint_cream', 'colors': [(187, 247, 208), (209, 250, 229)], 'category': 'pastel'},
    {'name': 'lavender_soft', 'colors': [(221, 214, 254), (233, 213, 255)], 'category': 'pastel'},
    
    # Neon Cyberpunk
    {'name': 'cyber_blue', 'colors': [(0, 255, 255), (0, 150, 255)], 'category': 'neon'},
    {'name': 'cyber_pink', 'colors': [(255, 0, 128), (255, 100, 200)], 'category': 'neon'},
    {'name': 'cyber_green', 'colors': [(0, 255, 128), (0, 200, 100)], 'category': 'neon'},
    {'name': 'cyber_purple', 'colors': [(128, 0, 255), (200, 100, 255)], 'category': 'neon'},
    
    # Earth Tones
    {'name': 'sand', 'colors': [(210, 180, 140), (245, 222, 179)], 'category': 'earth'},
    {'name': 'clay', 'colors': [(188, 143, 127), (210, 180, 140)], 'category': 'earth'},
    {'name': 'stone', 'colors': [(120, 120, 120), (180, 180, 180)], 'category': 'earth'},
    {'name': 'wood', 'colors': [(139, 90, 43), (210, 180, 140)], 'category': 'earth'},
    
    # Tech Modern
    {'name': 'tech_blue', 'colors': [(0, 123, 255), (0, 188, 212)], 'category': 'tech'},
    {'name': 'digital', 'colors': [(0, 150, 136), (76, 175, 80)], 'category': 'tech'},
    {'name': 'circuit', 'colors': [(63, 81, 181), (3, 169, 244)], 'category': 'tech'},
    {'name': 'startup', 'colors': [(255, 87, 34), (255, 193, 7)], 'category': 'tech'},
]


def generate_background_library(output_dir, count_per_palette=3):
    """
    Generate a complete background library.
    For each color palette, create multiple variations with different styles.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    width, height = 1080, 1080
    total_generated = 0
    
    print("=" * 70)
    print("GENERATING PROFESSIONAL BACKGROUND LIBRARY")
    print("=" * 70)
    print(f"\n📐 Size: {width}x{height}")
    print(f"🎨 Palettes: {len(COLOR_PALETTES)}")
    print(f"📑 Per palette: {count_per_palette}")
    print(f"📊 Total backgrounds: {len(COLOR_PALETTES) * count_per_palette}")
    
    for palette_idx, palette in enumerate(COLOR_PALETTES, 1):
        print(f"\n{'='*70}")
        print(f"Palette {palette_idx}/{len(COLOR_PALETTES)}: {palette['name']} ({palette['category']})")
        print(f"{'='*70}")
        
        for variation in range(count_per_palette):
            # Randomly select style based on category
            category = palette['category']
            
            if category in ['corporate', 'minimal']:
                styles = ['vertical', 'horizontal', 'radial', 'grid', 'dots']
                style = random.choice(styles)
                if style in ['vertical', 'horizontal', 'radial']:
                    bg = generate_gradient_background(width, height, style, palette['colors'])
                else:
                    bg = generate_geometric_background(width, height, style, palette['colors'])
            elif category in ['abstract', 'neon']:
                styles = ['waves', 'blur_orbs', 'mesh', 'diagonal']
                style = random.choice(styles)
                if style == 'diagonal':
                    bg = generate_gradient_background(width, height, 'diagonal', palette['colors'])
                else:
                    bg = generate_abstract_background(width, height, style, palette['colors'])
            elif category in ['luxury', 'warm']:
                styles = ['radial', 'diagonal', 'mesh', 'blur_orbs']
                style = random.choice(styles)
                if style in ['radial', 'diagonal']:
                    bg = generate_gradient_background(width, height, style, palette['colors'])
                else:
                    bg = generate_abstract_background(width, height, style, palette['colors'])
            else:
                styles = ['vertical', 'horizontal', 'radial', 'dots', 'circles']
                style = random.choice(styles)
                if style in ['vertical', 'horizontal', 'radial']:
                    bg = generate_gradient_background(width, height, style, palette['colors'])
                else:
                    bg = generate_geometric_background(width, height, style, palette['colors'])
            
            # Save background
            filename = f"bg_{palette['category']}_{palette['name']}_v{variation+1}.png"
            filepath = os.path.join(output_dir, filename)
            bg.save(filepath, 'PNG', quality=95, optimize=True)
            
            file_size = os.path.getsize(filepath) / 1024
            print(f"  ✓ {filename} ({file_size:.1f}KB)")
            total_generated += 1
    
    print("\n" + "=" * 70)
    print(f"✅ BACKGROUND LIBRARY COMPLETE!")
    print("=" * 70)
    print(f"\n📁 Location: {output_dir}")
    print(f"📊 Total backgrounds: {total_generated}")
    print(f"\n🎨 Categories:")
    
    # Count by category
    categories = {}
    for palette in COLOR_PALETTES:
        cat = palette['category']
        categories[cat] = categories.get(cat, 0) + count_per_palette
    
    for cat, count in sorted(categories.items()):
        print(f"   - {cat}: {count} backgrounds")
    
    print("=" * 70)


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), 'data', 'outputs', 'backgrounds')
    generate_background_library(output_dir, count_per_palette=3)
