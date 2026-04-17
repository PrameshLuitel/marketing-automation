"""
Enhanced Image Generator - 50+ Professional Design Templates
Uses company profile assets (logo, product images) randomly
Generates multiple high-quality marketing design variations
"""
import os
import sys
import random
import math
import asyncio
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from loguru import logger

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Global progress tracker
IMAGE_PROGRESS = {}


# ── Font Loading ──────────────────────────────────────────
def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load the best available system font."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple:
    """Convert hex color string to RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r, g, b, alpha)


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = font.getbbox(test)
        if bbox[2] > max_width and current_line:
            lines.append(current_line.strip())
            current_line = word
        else:
            current_line = test
    if current_line.strip():
        lines.append(current_line.strip())
    return lines if lines else [text]


# ── 50+ Professional Layout Templates ────────────────────
# Organized by style: corporate, minimal, abstract, neon, luxury
LAYOUTS = [
    # CORPORATE SERIES (1-10)
    {"id": "corp-top-hero", "headline_y_ratio": 0.25, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.0, "grad_direction": "top", "grad_opacity": 0.5, "accent_y_offset": -20, "accent_width": 80, "company_bar": True},
    {"id": "corp-left-editorial", "headline_y_ratio": 0.35, "text_x_ratio": 0.08, "align": "left", "font_scale": 1.1, "grad_direction": "left", "grad_opacity": 0.6, "accent_y_offset": -30, "accent_width": 90, "company_bar": True},
    {"id": "corp-right-exec", "headline_y_ratio": 0.35, "text_x_ratio": 0.92, "align": "right", "font_scale": 0.95, "grad_direction": "right", "grad_opacity": 0.55, "accent_y_offset": -25, "accent_width": 120, "company_bar": True},
    {"id": "corp-center-bold", "headline_y_ratio": 0.45, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.2, "grad_direction": "center", "grad_opacity": 0.65, "accent_y_offset": -35, "accent_width": 100, "company_bar": False},
    {"id": "corp-bottom-cta", "headline_y_ratio": 0.65, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.9, "grad_direction": "bottom", "grad_opacity": 0.7, "accent_y_offset": -28, "accent_width": 110, "company_bar": True},
    {"id": "corp-top-left", "headline_y_ratio": 0.20, "text_x_ratio": 0.06, "align": "left", "font_scale": 1.05, "grad_direction": "top-left", "grad_opacity": 0.5, "accent_y_offset": -22, "accent_width": 75, "company_bar": True},
    {"id": "corp-top-right", "headline_y_ratio": 0.22, "text_x_ratio": 0.94, "align": "right", "font_scale": 0.98, "grad_direction": "top-right", "grad_opacity": 0.48, "accent_y_offset": -24, "accent_width": 85, "company_bar": True},
    {"id": "corp-mid-left", "headline_y_ratio": 0.50, "text_x_ratio": 0.05, "align": "left", "font_scale": 1.15, "grad_direction": "left", "grad_opacity": 0.62, "accent_y_offset": -32, "accent_width": 95, "company_bar": False},
    {"id": "corp-mid-right", "headline_y_ratio": 0.48, "text_x_ratio": 0.95, "align": "right", "font_scale": 1.08, "grad_direction": "right", "grad_opacity": 0.58, "accent_y_offset": -30, "accent_width": 105, "company_bar": True},
    {"id": "corp-diagonal", "headline_y_ratio": 0.40, "text_x_ratio": 0.10, "align": "left", "font_scale": 1.0, "grad_direction": "diagonal", "grad_opacity": 0.55, "accent_y_offset": -26, "accent_width": 88, "company_bar": True},
    
    # MINIMAL SERIES (11-20)
    {"id": "min-center-zen", "headline_y_ratio": 0.50, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.85, "grad_direction": "center", "grad_opacity": 0.3, "accent_y_offset": -18, "accent_width": 60, "company_bar": False},
    {"id": "min-top-space", "headline_y_ratio": 0.18, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.9, "grad_direction": "top", "grad_opacity": 0.25, "accent_y_offset": -15, "accent_width": 50, "company_bar": True},
    {"id": "min-bottom-clean", "headline_y_ratio": 0.75, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.88, "grad_direction": "bottom", "grad_opacity": 0.28, "accent_y_offset": -16, "accent_width": 55, "company_bar": True},
    {"id": "min-left-zen", "headline_y_ratio": 0.30, "text_x_ratio": 0.12, "align": "left", "font_scale": 0.92, "grad_direction": "left", "grad_opacity": 0.32, "accent_y_offset": -20, "accent_width": 70, "company_bar": False},
    {"id": "min-right-airy", "headline_y_ratio": 0.32, "text_x_ratio": 0.88, "align": "right", "font_scale": 0.87, "grad_direction": "right", "grad_opacity": 0.27, "accent_y_offset": -17, "accent_width": 65, "company_bar": True},
    {"id": "min-corner", "headline_y_ratio": 0.15, "text_x_ratio": 0.05, "align": "left", "font_scale": 0.82, "grad_direction": "top-left", "grad_opacity": 0.22, "accent_y_offset": -12, "accent_width": 45, "company_bar": False},
    {"id": "min-vertical", "headline_y_ratio": 0.50, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.95, "grad_direction": "vertical", "grad_opacity": 0.35, "accent_y_offset": -21, "accent_width": 72, "company_bar": True},
    {"id": "min-asymmetric", "headline_y_ratio": 0.38, "text_x_ratio": 0.15, "align": "left", "font_scale": 1.0, "grad_direction": "left", "grad_opacity": 0.30, "accent_y_offset": -19, "accent_width": 68, "company_bar": False},
    {"id": "min-floating", "headline_y_ratio": 0.42, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.91, "grad_direction": "center", "grad_opacity": 0.26, "accent_y_offset": -14, "accent_width": 58, "company_bar": True},
    {"id": "min-edge", "headline_y_ratio": 0.28, "text_x_ratio": 0.92, "align": "right", "font_scale": 0.86, "grad_direction": "right", "grad_opacity": 0.24, "accent_y_offset": -13, "accent_width": 48, "company_bar": True},
    
    # ABSTRACT SERIES (21-30)
    {"id": "abs-top-hero", "headline_y_ratio": 0.25, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.15, "grad_direction": "top", "grad_opacity": 0.7, "accent_y_offset": -35, "accent_width": 130, "company_bar": False},
    {"id": "abs-bottom-drama", "headline_y_ratio": 0.70, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.1, "grad_direction": "bottom", "grad_opacity": 0.75, "accent_y_offset": -38, "accent_width": 140, "company_bar": True},
    {"id": "abs-left-canvas", "headline_y_ratio": 0.40, "text_x_ratio": 0.08, "align": "left", "font_scale": 1.05, "grad_direction": "left", "grad_opacity": 0.65, "accent_y_offset": -32, "accent_width": 115, "company_bar": False},
    {"id": "abs-right-gallery", "headline_y_ratio": 0.38, "text_x_ratio": 0.92, "align": "right", "font_scale": 1.0, "grad_direction": "right", "grad_opacity": 0.68, "accent_y_offset": -34, "accent_width": 125, "company_bar": True},
    {"id": "abs-center-pop", "headline_y_ratio": 0.48, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.25, "grad_direction": "radial", "grad_opacity": 0.8, "accent_y_offset": -40, "accent_width": 150, "company_bar": False},
    {"id": "abs-diagonal", "headline_y_ratio": 0.35, "text_x_ratio": 0.10, "align": "left", "font_scale": 1.08, "grad_direction": "diagonal", "grad_opacity": 0.72, "accent_y_offset": -36, "accent_width": 135, "company_bar": True},
    {"id": "abs-split", "headline_y_ratio": 0.50, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.12, "grad_direction": "split", "grad_opacity": 0.78, "accent_y_offset": -37, "accent_width": 145, "company_bar": False},
    {"id": "abs-corner", "headline_y_ratio": 0.20, "text_x_ratio": 0.06, "align": "left", "font_scale": 0.98, "grad_direction": "top-left", "grad_opacity": 0.62, "accent_y_offset": -30, "accent_width": 110, "company_bar": True},
    {"id": "abs-wave", "headline_y_ratio": 0.55, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.18, "grad_direction": "wave", "grad_opacity": 0.74, "accent_y_offset": -39, "accent_width": 155, "company_bar": False},
    {"id": "abs-geometric", "headline_y_ratio": 0.42, "text_x_ratio": 0.88, "align": "right", "font_scale": 1.02, "grad_direction": "right", "grad_opacity": 0.66, "accent_y_offset": -31, "accent_width": 120, "company_bar": True},
    
    # NEON SERIES (31-40)
    {"id": "neon-glow-top", "headline_y_ratio": 0.28, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.2, "grad_direction": "top", "grad_opacity": 0.85, "accent_y_offset": -40, "accent_width": 160, "company_bar": False},
    {"id": "neon-circuit-left", "headline_y_ratio": 0.45, "text_x_ratio": 0.08, "align": "left", "font_scale": 1.1, "grad_direction": "left", "grad_opacity": 0.9, "accent_y_offset": -42, "accent_width": 170, "company_bar": True},
    {"id": "neon-cyber-right", "headline_y_ratio": 0.42, "text_x_ratio": 0.92, "align": "right", "font_scale": 1.05, "grad_direction": "right", "grad_opacity": 0.88, "accent_y_offset": -41, "accent_width": 165, "company_bar": False},
    {"id": "neon-matrix", "headline_y_ratio": 0.50, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.25, "grad_direction": "matrix", "grad_opacity": 0.92, "accent_y_offset": -45, "accent_width": 180, "company_bar": True},
    {"id": "neon-pulse", "headline_y_ratio": 0.68, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.15, "grad_direction": "bottom", "grad_opacity": 0.86, "accent_y_offset": -38, "accent_width": 155, "company_bar": False},
    {"id": "neon-grid", "headline_y_ratio": 0.38, "text_x_ratio": 0.10, "align": "left", "font_scale": 1.08, "grad_direction": "grid", "grad_opacity": 0.84, "accent_y_offset": -36, "accent_width": 148, "company_bar": True},
    {"id": "neon-laser", "headline_y_ratio": 0.35, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.22, "grad_direction": "diagonal", "grad_opacity": 0.91, "accent_y_offset": -43, "accent_width": 175, "company_bar": False},
    {"id": "neon-vapor", "headline_y_ratio": 0.52, "text_x_ratio": 0.88, "align": "right", "font_scale": 1.12, "grad_direction": "vapor", "grad_opacity": 0.87, "accent_y_offset": -39, "accent_width": 162, "company_bar": True},
    {"id": "neon-rain", "headline_y_ratio": 0.30, "text_x_ratio": 0.06, "align": "left", "font_scale": 1.0, "grad_direction": "rain", "grad_opacity": 0.82, "accent_y_offset": -34, "accent_width": 140, "company_bar": False},
    {"id": "neon-holo", "headline_y_ratio": 0.48, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.28, "grad_direction": "hologram", "grad_opacity": 0.93, "accent_y_offset": -46, "accent_width": 185, "company_bar": True},
    
    # LUXURY SERIES (41-50)
    {"id": "lux-elegant", "headline_y_ratio": 0.45, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.95, "grad_direction": "center", "grad_opacity": 0.45, "accent_y_offset": -28, "accent_width": 95, "company_bar": True},
    {"id": "lux-gold-top", "headline_y_ratio": 0.22, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.0, "grad_direction": "top", "grad_opacity": 0.5, "accent_y_offset": -30, "accent_width": 105, "company_bar": False},
    {"id": "lux-fashion", "headline_y_ratio": 0.38, "text_x_ratio": 0.90, "align": "right", "font_scale": 0.92, "grad_direction": "right", "grad_opacity": 0.48, "accent_y_offset": -26, "accent_width": 88, "company_bar": True},
    {"id": "lux-editorial", "headline_y_ratio": 0.32, "text_x_ratio": 0.10, "align": "left", "font_scale": 1.05, "grad_direction": "left", "grad_opacity": 0.52, "accent_y_offset": -32, "accent_width": 110, "company_bar": False},
    {"id": "lux-premium", "headline_y_ratio": 0.72, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.88, "grad_direction": "bottom", "grad_opacity": 0.46, "accent_y_offset": -24, "accent_width": 82, "company_bar": True},
    {"id": "lux-sophisticated", "headline_y_ratio": 0.50, "text_x_ratio": 0.5, "align": "center", "font_scale": 0.98, "grad_direction": "sophisticated", "grad_opacity": 0.44, "accent_y_offset": -29, "accent_width": 98, "company_bar": True},
    {"id": "lux-blackcard", "headline_y_ratio": 0.40, "text_x_ratio": 0.08, "align": "left", "font_scale": 1.02, "grad_direction": "card", "grad_opacity": 0.54, "accent_y_offset": -31, "accent_width": 108, "company_bar": False},
    {"id": "lux-platinum", "headline_y_ratio": 0.48, "text_x_ratio": 0.92, "align": "right", "font_scale": 0.96, "grad_direction": "platinum", "grad_opacity": 0.47, "accent_y_offset": -27, "accent_width": 92, "company_bar": True},
    {"id": "lux-diamond", "headline_y_ratio": 0.35, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.08, "grad_direction": "diamond", "grad_opacity": 0.51, "accent_y_offset": -33, "accent_width": 115, "company_bar": False},
    {"id": "lux-royal", "headline_y_ratio": 0.42, "text_x_ratio": 0.5, "align": "center", "font_scale": 1.0, "grad_direction": "royal", "grad_opacity": 0.49, "accent_y_offset": -30, "accent_width": 100, "company_bar": True},
]


# ── Gradient Generators ───────────────────────────────────
def _apply_gradient(canvas: Image.Image, direction: str, opacity: float, accent_color: tuple):
    """Apply a directional gradient overlay to the canvas."""
    W, H = canvas.size
    gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)

    if direction in ("top", "top-left", "top-right"):
        for y in range(int(H * 0.6)):
            alpha = int(opacity * 255 * (1 - y / (H * 0.6)))
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    elif direction in ("bottom",):
        start = int(H * 0.35)
        span = H - start
        for y in range(start, H):
            alpha = int(opacity * 255 * ((y - start) / span))
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    elif direction in ("left",):
        for x in range(int(W * 0.55)):
            alpha = int(opacity * 255 * (1 - x / (W * 0.55)))
            draw.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    elif direction in ("right",):
        start = int(W * 0.45)
        span = W - start
        for x in range(start, W):
            alpha = int(opacity * 255 * ((x - start) / span))
            draw.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    elif direction in ("center", "radial", "sophisticated", "diamond", "platinum", "royal"):
        cx, cy = W // 2, H // 2
        max_r = int(math.sqrt(cx ** 2 + cy ** 2))
        for r in range(max_r, 0, -4):
            alpha = int(opacity * 255 * (1 - r / max_r))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0, 0, 0, alpha))
    elif direction in ("diagonal", "split", "vapor", "card"):
        for i in range(int((W + H) * 0.6)):
            alpha = int(opacity * 255 * (1 - i / (W * 0.6)))
            draw.line([(0, i), (i, 0)], fill=(0, 0, 0, alpha))
    else:
        # Default: top gradient
        for y in range(int(H * 0.6)):
            alpha = int(opacity * 255 * (1 - y / (H * 0.6)))
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))

    canvas = Image.alpha_composite(canvas, gradient)
    return canvas


# ── Background Generators ─────────────────────────────────
def _generate_gradient_background(W: int, H: int, primary: str, secondary: str, theme: str) -> Image.Image:
    """Generate a premium gradient background based on theme - HIGHLY DIVERSE."""
    p_rgba = _hex_to_rgba(primary)
    s_rgba = _hex_to_rgba(secondary)

    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)

    # Randomly select background style for more variety
    bg_style = random.choice(['gradient', 'solid', 'split', 'radial', 'diagonal'])

    if theme in ("corporate", "minimal"):
        # Clean white-to-light gradient variations
        if bg_style == 'gradient':
            # Vertical gradient
            for y in range(H):
                ratio = y / H
                r = int(245 + (235 - 245) * ratio)
                g = int(245 + (238 - 245) * ratio)
                b = int(250 + (242 - 250) * ratio)
                draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        elif bg_style == 'solid':
            # Clean white/off-white solid
            draw.rectangle([0, 0, W, H], fill=(248, 248, 250, 255))
        elif bg_style == 'split':
            # Split background - white left, light gray right
            draw.rectangle([0, 0, W//2, H], fill=(250, 250, 252, 255))
            draw.rectangle([W//2, 0, W, H], fill=(240, 240, 245, 255))
        elif bg_style == 'radial':
            # Radial white-to-gray
            for y in range(H):
                for x in range(0, W, 2):
                    dist = ((x - W//2)**2 + (y - H//2)**2) ** 0.5
                    max_dist = ((W//2)**2 + (H//2)**2) ** 0.5
                    ratio = dist / max_dist
                    val = int(255 - 20 * ratio)
                    draw.point((x, y), fill=(val, val, val+2, 255))
        else:  # diagonal
            for y in range(H):
                for x in range(W):
                    ratio = (x + y) / (W + H)
                    val = int(250 - 15 * ratio)
                    draw.point((x, y), fill=(val, val, val+3, 255))
        
        # Subtle colored accent shapes
        accent = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        adraw = ImageDraw.Draw(accent)
        accent_style = random.choice(['circle', 'bars', 'dots', 'none'])
        
        if accent_style == 'circle':
            cx, cy = int(W * random.uniform(0.6, 0.8)), int(H * random.uniform(0.2, 0.4))
            for r_radius in range(400, 0, -2):
                alpha = max(0, int(30 * (1 - r_radius / 400)))
                adraw.ellipse([cx - r_radius, cy - r_radius, cx + r_radius, cy + r_radius],
                              fill=(p_rgba[0], p_rgba[1], p_rgba[2], alpha))
        elif accent_style == 'bars':
            for i in range(5):
                bar_y = int(H * 0.2 + i * H * 0.15)
                bar_h = random.randint(20, 50)
                adraw.rectangle([0, bar_y, W, bar_y + bar_h], 
                               fill=(p_rgba[0], p_rgba[1], p_rgba[2], 8))
        elif accent_style == 'dots':
            for _ in range(50):
                dx, dy = random.randint(0, W), random.randint(0, H)
                adraw.ellipse([dx-3, dy-3, dx+3, dy+3], 
                             fill=(p_rgba[0], p_rgba[1], p_rgba[2], 20))
        
        img = Image.alpha_composite(img, accent)

    elif theme == "abstract":
        # Dark gradient with colorful orbs - MULTIPLE STYLES
        if bg_style == 'gradient':
            for y in range(H):
                ratio = y / H
                r = int(8 + 12 * ratio)
                g = int(8 + 10 * ratio)
                b = int(15 + 20 * ratio)
                draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        elif bg_style == 'solid':
            draw.rectangle([0, 0, W, H], fill=(12, 10, 20, 255))
        elif bg_style == 'split':
            draw.rectangle([0, 0, W//2, H], fill=(10, 8, 18, 255))
            draw.rectangle([W//2, 0, W, H], fill=(15, 12, 22, 255))
        elif bg_style == 'radial':
            for y in range(H):
                for x in range(0, W, 2):
                    dist = ((x - W//2)**2 + (y - H//2)**2) ** 0.5
                    max_dist = ((W//2)**2 + (H//2)**2) ** 0.5
                    ratio = dist / max_dist
                    r = int(8 + 15 * ratio)
                    g = int(8 + 12 * ratio)
                    b = int(15 + 25 * ratio)
                    draw.point((x, y), fill=(r, g, b, 255))
        else:  # diagonal
            for y in range(H):
                for x in range(W):
                    ratio = (x + y) / (W + H)
                    r = int(8 + 12 * ratio)
                    g = int(8 + 10 * ratio)
                    b = int(15 + 20 * ratio)
                    draw.point((x, y), fill=(r, g, b, 255))
        
        # Add color orbs - VARIED PATTERNS
        orb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(orb)
        
        orb_pattern = random.choice(['triple', 'dual', 'single-large', 'scattered'])
        
        if orb_pattern == 'triple':
            orb_configs = [
                (int(W * 0.2), int(H * 0.25), 350, p_rgba),
                (int(W * 0.8), int(H * 0.7), 300, s_rgba),
                (int(W * 0.5), int(H * 0.5), 250, (p_rgba[0], s_rgba[1], p_rgba[2], 255)),
            ]
        elif orb_pattern == 'dual':
            orb_configs = [
                (int(W * 0.3), int(H * 0.3), 400, p_rgba),
                (int(W * 0.7), int(H * 0.7), 380, s_rgba),
            ]
        elif orb_pattern == 'single-large':
            orb_configs = [
                (int(W * 0.5), int(H * 0.5), 500, p_rgba),
            ]
        else:  # scattered
            orb_configs = []
            for _ in range(8):
                cx = random.randint(100, W-100)
                cy = random.randint(100, H-100)
                radius = random.randint(150, 300)
                color = random.choice([p_rgba, s_rgba, (s_rgba[0], p_rgba[1], s_rgba[2], 255)])
                orb_configs.append((cx, cy, radius, color))
        
        for cx, cy, max_r, color in orb_configs:
            for r_radius in range(max_r, 0, -3):
                alpha = max(0, int(45 * (1 - r_radius / max_r)))
                odraw.ellipse([cx - r_radius, cy - r_radius, cx + r_radius, cy + r_radius],
                              fill=(color[0], color[1], color[2], alpha))
        img = Image.alpha_composite(img, orb)
        
        # Optional grid overlay
        if random.random() > 0.5:
            grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(grid)
            grid_spacing = random.choice([30, 40, 50, 60])
            for gx in range(0, W, grid_spacing):
                gdraw.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 8))
            for gy in range(0, H, grid_spacing):
                gdraw.line([(0, gy), (W, gy)], fill=(255, 255, 255, 8))
            img = Image.alpha_composite(img, grid)

    elif theme == "neon":
        # Deep black with neon accents
        for y in range(H):
            draw.line([(0, y), (W, y)], fill=(5, 5, 10, 255))
        # Neon streaks
        neon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ndraw = ImageDraw.Draw(neon)
        for i in range(3):
            x = int(W * (0.2 + i * 0.3))
            ndraw.line([(x, 0), (x, H)], fill=(p_rgba[0], p_rgba[1], p_rgba[2], 40), width=2)
        for r_radius in range(200, 0, -4):
            alpha = max(0, int(35 * (1 - r_radius / 200)))
            ndraw.ellipse([int(W*0.5) - r_radius, int(H*0.5) - r_radius, int(W*0.5) + r_radius, int(H*0.5) + r_radius],
                          fill=(s_rgba[0], s_rgba[1], s_rgba[2], alpha))
        img = Image.alpha_composite(img, neon)

    elif theme == "luxury":
        # Rich dark gradient with gold/silver accents
        for y in range(H):
            ratio = y / H
            r = int(15 + 20 * ratio)
            g = int(12 + 18 * ratio)
            b = int(18 + 22 * ratio)
            draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        # Elegant accent
        lux = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(lux)
        cx, cy = int(W * 0.5), int(H * 0.4)
        for r_radius in range(300, 0, -3):
            alpha = max(0, int(40 * (1 - r_radius / 300)))
            ldraw.ellipse([cx - r_radius, cy - r_radius, cx + r_radius, cy + r_radius],
                          fill=(p_rgba[0], p_rgba[1], p_rgba[2], alpha))
        img = Image.alpha_composite(img, lux)

    return img


# ── Image Composition ─────────────────────────────────────
def _add_logo(canvas: Image.Image, logo_path: str) -> Image.Image:
    """Add company logo to the canvas."""
    try:
        logo = Image.open(logo_path).convert("RGBA")
        # Resize logo to reasonable size
        logo.thumbnail((150, 150))
        # Place in top-right corner
        x = canvas.width - logo.width - 30
        y = 30
        canvas.paste(logo, (x, y), logo)
    except Exception as e:
        logger.warning(f"Failed to add logo: {e}")
    return canvas


def _add_product_images(canvas: Image.Image, product_paths: list, max_images: int = 4) -> Image.Image:
    """Randomly add product images to the canvas - LARGE and prominent."""
    if not product_paths:
        return canvas
    
    # Select random subset of product images (1 to max_images)
    num_to_add = min(random.randint(1, max_images), len(product_paths))
    selected_products = random.sample(product_paths, num_to_add)
    
    for i, prod_path in enumerate(selected_products):
        try:
            prod_img = Image.open(prod_path).convert("RGBA")
            # MUCH LARGER product images - 500-700px instead of 200-400px
            prod_size = random.randint(500, 700)
            prod_img.thumbnail((prod_size, prod_size), Image.Resampling.LANCZOS)
            
            # Diverse placement options - covering more of the canvas
            placements = [
                # Center placements (prominent)
                (canvas.width // 2 - prod_img.width // 2, canvas.height // 2 - prod_img.height // 2),
                (canvas.width // 2 - prod_img.width // 2, canvas.height // 3 - prod_img.height // 2),
                # Side placements
                (30, canvas.height // 2 - prod_img.height // 2),  # left-center
                (canvas.width - prod_img.width - 30, canvas.height // 2 - prod_img.height // 2),  # right-center
                # Bottom placements
                (canvas.width // 2 - prod_img.width // 2, canvas.height - prod_img.height - 50),  # bottom-center
                (20, canvas.height - prod_img.height - 40),  # bottom-left
                (canvas.width - prod_img.width - 20, canvas.height - prod_img.height - 40),  # bottom-right
                # Top placements
                (canvas.width // 2 - prod_img.width // 2, 80),  # top-center
                # Diagonal placements
                (50, 50),  # top-left
                (canvas.width - prod_img.width - 50, 50),  # top-right
            ]
            x, y = random.choice(placements)
            
            # Add subtle shadow for depth
            shadow = prod_img.copy()
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))
            shadow_offset = 20
            canvas.paste(shadow, (x + shadow_offset, y + shadow_offset), shadow)
            
            # Paste the product image
            canvas.paste(prod_img, (x, y), prod_img)
            
        except Exception as e:
            logger.warning(f"Failed to add product image: {e}")
    
    return canvas


def _render_text_block(
    canvas: Image.Image,
    headline: str,
    tagline: str,
    layout: dict,
    primary_color: str,
    company_name: str = "",
):
    """Render headline, tagline, accent bar, and company name onto the canvas."""
    W, H = canvas.size
    draw = ImageDraw.Draw(canvas)

    # Compute sizes
    base_size = min(72, max(42, W // max(len(headline), 1)))
    headline_size = int(base_size * layout["font_scale"])
    tagline_size = max(20, headline_size // 3)

    headline_font = _load_font(headline_size, bold=True)
    tagline_font = _load_font(tagline_size, bold=False)
    company_font = _load_font(14, bold=True)

    # Text color based on theme
    text_color = (255, 255, 255, 255)
    tagline_color = (220, 220, 220, 230)

    # Position
    text_x = int(W * layout["text_x_ratio"])
    headline_y = int(H * layout["headline_y_ratio"])
    max_text_w = int(W * 0.82)
    align = layout["align"]

    # Wrap headline
    headline_lines = _wrap_text(headline.upper(), headline_font, max_text_w)
    line_height = headline_size + 8

    # Draw text shadow first
    shadow_offset = 3
    for i, line in enumerate(headline_lines):
        bbox = headline_font.getbbox(line)
        tw = bbox[2] - bbox[0]
        if align == "center":
            lx = text_x - tw // 2
        elif align == "right":
            lx = text_x - tw
        else:
            lx = text_x
        ly = headline_y + i * line_height
        # Shadow
        draw.text((lx + shadow_offset, ly + shadow_offset), line, font=headline_font, fill=(0, 0, 0, 140))
        # Main text
        draw.text((lx, ly), line, font=headline_font, fill=text_color)

    # Accent bar
    accent_color = _hex_to_rgba(primary_color)
    accent_y = headline_y + layout["accent_y_offset"]
    if align == "center":
        bar_x = text_x - layout["accent_width"] // 2
    elif align == "right":
        bar_x = text_x - layout["accent_width"]
    else:
        bar_x = text_x
    draw.rounded_rectangle(
        [bar_x, accent_y, bar_x + layout["accent_width"], accent_y + 5],
        radius=2,
        fill=accent_color
    )

    # Tagline
    tagline_y = headline_y + len(headline_lines) * line_height + 20
    tagline_lines = _wrap_text(tagline, tagline_font, max_text_w)
    for i, line in enumerate(tagline_lines):
        bbox = tagline_font.getbbox(line)
        tw = bbox[2] - bbox[0]
        if align == "center":
            lx = text_x - tw // 2
        elif align == "right":
            lx = text_x - tw
        else:
            lx = text_x
        ly = tagline_y + i * (tagline_size + 6)
        draw.text((lx + 1, ly + 1), line, font=tagline_font, fill=(0, 0, 0, 80))
        draw.text((lx, ly), line, font=tagline_font, fill=tagline_color)

    # Company name bar
    if company_name and layout.get("company_bar"):
        bar_h = 55
        bar_overlay = Image.new("RGBA", (W, bar_h), (0, 0, 0, 160))
        bar_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bar_img.paste(bar_overlay, (0, H - bar_h), bar_overlay)
        canvas = Image.alpha_composite(canvas, bar_img)
        
        bdraw = ImageDraw.Draw(canvas)
        bdraw.text((30, H - bar_h + 18), company_name.upper(), font=company_font, fill=(255, 255, 255, 255))

    return canvas


def compose_graphic(
    width: int,
    height: int,
    headline: str,
    tagline: str,
    primary_color: str,
    secondary_color: str,
    template_theme: str = "corporate",
    layout_seed: int = 0,
    company_name: str = "",
    logo_path: str = "",
    product_images: list = [],
) -> Image.Image:
    """Compose a SINGLE-LAYER marketing graphic (legacy - for backward compatibility)."""
    layout = LAYOUTS[layout_seed % len(LAYOUTS)]
    logger.info(f"[Composer] Layout: {layout['id']} | Theme: {template_theme} | {width}x{height}")

    # 1. Background
    canvas = _generate_gradient_background(width, height, primary_color, secondary_color, template_theme)

    # 2. Add product images (if available)
    if product_images:
        canvas = _add_product_images(canvas, product_images)

    # 3. Gradient overlay
    accent_rgba = _hex_to_rgba(primary_color)
    canvas = _apply_gradient(canvas, layout["grad_direction"], layout["grad_opacity"], accent_rgba)

    # 4. Text
    canvas = _render_text_block(canvas, headline, tagline, layout, primary_color, company_name)

    # 5. Logo
    if logo_path:
        canvas = _add_logo(canvas, logo_path)

    return canvas


def compose_graphic_layered(
    width: int,
    height: int,
    headline: str,
    tagline: str,
    primary_color: str,
    secondary_color: str,
    template_theme: str = "corporate",
    layout_seed: int = 0,
    company_name: str = "",
    logo_path: str = "",
    product_images: list = [],
    background_path: str = "",  # NEW: Pre-made background from library
) -> dict:
    """
    Create a LAYERED marketing graphic with separate components.
    Uses pre-made background from library if available, otherwise generates one.
    """
    layout = LAYOUTS[layout_seed % len(LAYOUTS)]
    logger.info(f"[Composer Layered] Layout: {layout['id']} | Theme: {template_theme} | {width}x{height}")
    
    layers = {}
    
    # Layer 1: Background (use pre-made if available, otherwise generate)
    if background_path and os.path.exists(background_path):
        logger.info(f"[Composer] Using pre-made background: {os.path.basename(background_path)}")
        bg_img = Image.open(background_path).convert('RGBA')
        bg_img = bg_img.resize((width, height), Image.Resampling.LANCZOS)
        layers['background'] = bg_img
    else:
        logger.info(f"[Composer] Generating background with theme: {template_theme}")
        layers['background'] = _generate_gradient_background(width, height, primary_color, secondary_color, template_theme)
    
    # Layer 2: Product images (if any)
    if product_images:
        product_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        product_layer = _add_product_images(product_layer, product_images)
        # Only add if something was actually placed
        if list(product_layer.getdata()) != [(0, 0, 0, 0)] * (width * height):
            layers['products'] = product_layer
    
    # Layer 3: Gradient overlay
    gradient_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    accent_rgba = _hex_to_rgba(primary_color)
    gradient_layer = _apply_gradient(gradient_layer, layout["grad_direction"], layout["grad_opacity"], accent_rgba)
    layers['gradient_overlay'] = gradient_layer
    
    # Layer 4: Text block
    text_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    text_layer = _render_text_block(text_layer, headline, tagline, layout, primary_color, company_name)
    layers['text'] = text_layer
    
    # Layer 5: Logo (if available)
    if logo_path:
        logo_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        logo_layer = _add_logo(logo_layer, logo_path)
        # Only add if logo was actually placed
        if list(logo_layer.getdata()) != [(0, 0, 0, 0)] * (width * height):
            layers['logo'] = logo_layer
    
    # Create flattened composite for preview
    composite = layers['background'].copy()
    for layer_name in ['products', 'gradient_overlay', 'text', 'logo']:
        if layer_name in layers:
            composite = Image.alpha_composite(composite, layers[layer_name])
    
    return {
        'layers': layers,
        'composite': composite,
        'layout': layout,
    }


# ── ImageGenerator Class (Pipeline Integration) ───────────
class ImageGenerator:
    """Generates 50+ professional marketing graphics variations."""

    def __init__(self, profile_data: dict, run_id: str = "default"):
        self.profile = profile_data.get("company", {})
        self.run_id = run_id
        self.backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.outputs_dir = os.path.join(self.backend_dir, "data", "outputs")
        os.makedirs(self.outputs_dir, exist_ok=True)

    def _update_progress(self, step: int, total: int, message: str, detail: str = ""):
        IMAGE_PROGRESS[self.run_id] = {
            "step": step, "total_steps": total,
            "message": message, "detail": detail,
            "percent": int((step / total) * 100),
        }
        logger.info(f"[Image:{self.run_id}] Step {step}/{total}: {message}")

    def _collect_company_assets(self) -> tuple:
        """Collect logo and product images from company profile."""
        logo_path = ""
        product_paths = []
        
        # Get logo
        raw_logo = self.profile.get("logo_url", "")
        if raw_logo and "/outputs/assets/" in raw_logo:
            filename = raw_logo.split("/")[-1].split("?")[0]
            local = os.path.join(self.backend_dir, "data", "outputs", "assets", filename)
            if os.path.exists(local):
                logo_path = local
                logger.info(f"[Image:{self.run_id}] Logo found: {logo_path}")
        
        # Get product images from profile
        product_images = self.profile.get("product_images", [])
        if isinstance(product_images, list):
            for prod_url in product_images:
                if isinstance(prod_url, str) and "/outputs/assets/" in prod_url:
                    filename = prod_url.split("/")[-1].split("?")[0]
                    local = os.path.join(self.backend_dir, "data", "outputs", "assets", filename)
                    if os.path.exists(local):
                        product_paths.append(local)
        
        logger.info(f"[Image:{self.run_id}] Found {len(product_paths)} product images")
        return logo_path, product_paths
    
    def _get_random_background(self) -> str:
        """Get a random pre-made background from the background library (156 backgrounds)."""
        backgrounds_dir = os.path.join(os.path.dirname(__file__), 'data', 'outputs', 'backgrounds')
        
        if not os.path.exists(backgrounds_dir):
            logger.warning("[Image] Background library not found, using generated background")
            return None
        
        # Get all background files
        bg_files = [f for f in os.listdir(backgrounds_dir) if f.endswith('.png')]
        
        if not bg_files:
            logger.warning("[Image] No backgrounds in library, using generated background")
            return None
        
        # Randomly select a background
        selected_bg = random.choice(bg_files)
        bg_path = os.path.join(backgrounds_dir, selected_bg)
        
        logger.info(f"[Image:{self.run_id}] Selected background from library: {selected_bg}")
        return bg_path

    async def generate_async(self, config: dict) -> dict:
        """
        Generate multiple design variations using company assets.
        config expects:
        {
          "graphics_config": { "headline", "tagline", "template_theme", "layout_seed" },
          "graphic_size": "square" | "portrait" | "both",
          "num_variations": int (default: 5)
        }
        """
        graphic_size = config.get("graphic_size", "both")
        gc = config.get("graphics_config", {})
        num_variations = config.get("num_variations", 5)  # Generate 5 variations by default

        headline = gc.get("headline", "Premium Campaign.")
        tagline = gc.get("tagline", "Elevate your brand.")
        
        # Collect company assets
        logo_path, product_paths = self._collect_company_assets()

        primary = self.profile.get("brand_primary_color", "#3B82F6")
        secondary = self.profile.get("brand_secondary_color", "#8B5CF6")
        company_name = self.profile.get("company_name", "")

        self._update_progress(1, num_variations, f"Generating {num_variations} professional designs...", "")

        results = []
        loop = asyncio.get_event_loop()

        # Generate multiple design variations
        for i in range(num_variations):
            try:
                # Random layout and theme for each variation
                layout_idx = random.randint(0, len(LAYOUTS) - 1)
                themes = ["corporate", "minimal", "abstract", "neon", "luxury"]
                theme = random.choice(themes)
                
                # Get random pre-made background from library (like Canva templates)
                bg_path = self._get_random_background()
                
                self._update_progress(i + 1, num_variations, 
                                     f"Creating design {i+1}/{num_variations}...", 
                                     f"Layout: {LAYOUTS[layout_idx]['id']}, Background: {os.path.basename(bg_path) if bg_path else 'Generated'}")

                # Determine sizes to generate
                sizes = []
                if graphic_size in ("square", "both"):
                    sizes.append(("sq", 1080, 1080))
                if graphic_size in ("portrait", "both"):
                    sizes.append(("pt", 1080, 1350))

                for size_suffix, width, height in sizes:
                    # Generate LAYERED design with pre-made background
                    layered_result = await loop.run_in_executor(None, lambda: compose_graphic_layered(
                        width, height, headline, tagline, primary, secondary,
                        theme, layout_idx, company_name, logo_path, product_paths,
                        bg_path  # Pass pre-made background
                    ))
                    
                    # Save flattened preview for gallery
                    filename = f"design_{size_suffix}_{self.run_id}_v{i+1}.png"
                    img_path = os.path.join(self.outputs_dir, filename)
                    
                    layered_result['composite'].save(img_path, "PNG", quality=95, optimize=True)
                    
                    if os.path.exists(img_path):
                        file_size = os.path.getsize(img_path)
                        logger.success(f"[Image:{self.run_id}] Saved: {filename} ({file_size/1024:.1f}KB)")
                        results.append(f"/outputs/{filename}")
                    
                    # Save individual layers for editing (like Canva)
                    layer_output_dir = os.path.join(self.outputs_dir, f"design_{size_suffix}_{self.run_id}_v{i+1}_layers")
                    os.makedirs(layer_output_dir, exist_ok=True)
                    
                    for layer_name, layer_img in layered_result['layers'].items():
                        layer_filename = f"{layer_name}.png"
                        layer_path = os.path.join(layer_output_dir, layer_filename)
                        layer_img.save(layer_path, "PNG")
                    
                    logger.info(f"[Image:{self.run_id}] Saved {len(layered_result['layers'])} editable layers")

            except Exception as e:
                logger.error(f"[Image:{self.run_id}] Variation {i+1} failed: {e}", exc_info=True)

        self._update_progress(num_variations, num_variations, 
                             f"Generated {len(results)} designs!", 
                             f"Using {len(product_paths)} product images")

        return {
            "type": "graphics",
            "image_urls": results,
        }
