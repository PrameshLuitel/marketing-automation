"""
Image Composer — Pillow-based premium marketing graphic generator.
Inspired by the Canva MCP sharp-based composition engine.
Produces standard PNG files that Photopea can directly edit.
No Remotion dependency — pure Python, fast, reliable.
"""

import os
import json
import math
import random
import asyncio
from io import BytesIO
from loguru import logger

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
except ImportError:
    logger.error("Pillow not installed. Run: pip install Pillow")
    raise

# Global progress tracker for image generation
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


# ── Layout Archetypes ─────────────────────────────────────
LAYOUTS = [
    {
        "id": "top-hero",
        "headline_y_ratio": 0.14,
        "text_x_ratio": 0.06,
        "align": "left",
        "font_scale": 1.2,
        "grad_direction": "top",
        "grad_opacity": 0.7,
        "accent_y_offset": -40,
        "accent_width": 120,
        "company_bar": True,
    },
    {
        "id": "center-statement",
        "headline_y_ratio": 0.35,
        "text_x_ratio": 0.5,
        "align": "center",
        "font_scale": 1.15,
        "grad_direction": "radial",
        "grad_opacity": 0.55,
        "accent_y_offset": -35,
        "accent_width": 100,
        "company_bar": True,
    },
    {
        "id": "bottom-billboard",
        "headline_y_ratio": 0.68,
        "text_x_ratio": 0.5,
        "align": "center",
        "font_scale": 1.1,
        "grad_direction": "bottom",
        "grad_opacity": 0.8,
        "accent_y_offset": -30,
        "accent_width": 120,
        "company_bar": False,
    },
    {
        "id": "left-editorial",
        "headline_y_ratio": 0.40,
        "text_x_ratio": 0.06,
        "align": "left",
        "font_scale": 1.0,
        "grad_direction": "left",
        "grad_opacity": 0.6,
        "accent_y_offset": -30,
        "accent_width": 90,
        "company_bar": True,
    },
    {
        "id": "right-luxury",
        "headline_y_ratio": 0.35,
        "text_x_ratio": 0.94,
        "align": "right",
        "font_scale": 0.95,
        "grad_direction": "right",
        "grad_opacity": 0.55,
        "accent_y_offset": -25,
        "accent_width": 120,
        "company_bar": True,
    },
    {
        "id": "bottom-left-cinema",
        "headline_y_ratio": 0.72,
        "text_x_ratio": 0.06,
        "align": "left",
        "font_scale": 1.15,
        "grad_direction": "bottom",
        "grad_opacity": 0.75,
        "accent_y_offset": -35,
        "accent_width": 100,
        "company_bar": False,
    },
]


# ── Gradient Generators ───────────────────────────────────
def _apply_gradient(canvas: Image.Image, direction: str, opacity: float, accent_color: tuple):
    """Apply a directional gradient overlay to the canvas."""
    W, H = canvas.size
    gradient = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(gradient)

    if direction == "top":
        for y in range(int(H * 0.6)):
            alpha = int(opacity * 255 * (1 - y / (H * 0.6)))
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    elif direction == "bottom":
        start = int(H * 0.35)
        span = H - start
        for y in range(start, H):
            alpha = int(opacity * 255 * ((y - start) / span))
            draw.line([(0, y), (W, y)], fill=(0, 0, 0, alpha))
    elif direction == "left":
        for x in range(int(W * 0.55)):
            alpha = int(opacity * 255 * (1 - x / (W * 0.55)))
            draw.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    elif direction == "right":
        start = int(W * 0.45)
        span = W - start
        for x in range(start, W):
            alpha = int(opacity * 255 * ((x - start) / span))
            draw.line([(x, 0), (x, H)], fill=(0, 0, 0, alpha))
    elif direction == "radial":
        cx, cy = W // 2, H // 2
        max_r = math.sqrt(cx ** 2 + cy ** 2)
        for y in range(H):
            for x in range(0, W, 4):  # step 4 for performance
                r = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                alpha = int(opacity * 255 * min(1.0, r / max_r))
                draw.rectangle([x, y, x + 3, y], fill=(0, 0, 0, alpha))

    # Vignette (always)
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    cx, cy = W // 2, H // 2
    max_r = math.sqrt(cx ** 2 + cy ** 2)
    for ring in range(0, int(max_r), 6):
        alpha = int(100 * (ring / max_r) ** 2)
        vdraw.ellipse([cx - ring, cy - ring, cx + ring, cy + ring], outline=(0, 0, 0, min(alpha, 100)))

    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), gradient), (0, 0))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), vignette), (0, 0))
    return canvas


# ── Background Generators ─────────────────────────────────
def _generate_gradient_background(W: int, H: int, primary: str, secondary: str, theme: str) -> Image.Image:
    """Generate a premium gradient background based on theme."""
    p_rgba = _hex_to_rgba(primary)
    s_rgba = _hex_to_rgba(secondary)

    img = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(img)

    if theme in ("corporate", "minimal"):
        # Clean white-to-light gradient
        for y in range(H):
            ratio = y / H
            r = int(245 + (235 - 245) * ratio)
            g = int(245 + (238 - 245) * ratio)
            b = int(250 + (242 - 250) * ratio)
            draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        # Subtle colored accent circle
        accent = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        adraw = ImageDraw.Draw(accent)
        cx, cy = int(W * 0.7), int(H * 0.3)
        for r_radius in range(400, 0, -2):
            alpha = max(0, int(30 * (1 - r_radius / 400)))
            adraw.ellipse([cx - r_radius, cy - r_radius, cx + r_radius, cy + r_radius],
                          fill=(p_rgba[0], p_rgba[1], p_rgba[2], alpha))
        img = Image.alpha_composite(img, accent)

    elif theme == "abstract":
        # Dark gradient with colorful orbs
        for y in range(H):
            ratio = y / H
            r = int(8 + 12 * ratio)
            g = int(8 + 10 * ratio)
            b = int(15 + 20 * ratio)
            draw.line([(0, y), (W, y)], fill=(r, g, b, 255))
        # Add color orbs
        orb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(orb)
        orb_configs = [
            (int(W * 0.2), int(H * 0.25), 350, p_rgba),
            (int(W * 0.8), int(H * 0.7), 300, s_rgba),
            (int(W * 0.5), int(H * 0.5), 250, (p_rgba[0], s_rgba[1], p_rgba[2], 255)),
        ]
        for cx, cy, max_r, color in orb_configs:
            for r_radius in range(max_r, 0, -3):
                alpha = max(0, int(45 * (1 - r_radius / max_r)))
                odraw.ellipse([cx - r_radius, cy - r_radius, cx + r_radius, cy + r_radius],
                              fill=(color[0], color[1], color[2], alpha))
        img = Image.alpha_composite(img, orb)
        # Grid overlay
        grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(grid)
        for gx in range(0, W, 40):
            gdraw.line([(gx, 0), (gx, H)], fill=(255, 255, 255, 8))
        for gy in range(0, H, 40):
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
            ndraw.ellipse([W // 2 - r_radius, H // 2 - r_radius, W // 2 + r_radius, H // 2 + r_radius],
                          fill=(s_rgba[0], s_rgba[1], s_rgba[2], alpha))
        img = Image.alpha_composite(img, neon)

    else:
        # Default: elegant diagonal gradient
        for y in range(H):
            for x in range(0, W, 4):
                ratio = (x / W + y / H) / 2
                r = int(p_rgba[0] * (1 - ratio) + s_rgba[0] * ratio)
                g = int(p_rgba[1] * (1 - ratio) + s_rgba[1] * ratio)
                b = int(p_rgba[2] * (1 - ratio) + s_rgba[2] * ratio)
                draw.rectangle([x, y, x + 3, y], fill=(r, g, b, 255))

    return img


# ── Text Renderer ─────────────────────────────────────────
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

    # Determine text color based on background luminance
    # For abstract/neon themes use white, for corporate use dark
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
        canvas.paste(Image.alpha_composite(
            canvas.crop((0, H - bar_h, W, H)).convert("RGBA"),
            bar_overlay
        ), (0, H - bar_h))
        draw = ImageDraw.Draw(canvas)  # Refresh draw after paste
        comp_text = company_name.upper()
        bbox = company_font.getbbox(comp_text)
        tw = bbox[2] - bbox[0]
        draw.text(
            (W // 2 - tw // 2, H - bar_h // 2 - 7),
            comp_text,
            font=company_font,
            fill=(255, 255, 255, 220)
        )

    return canvas


# ── Logo Renderer ─────────────────────────────────────────
def _add_logo(canvas: Image.Image, logo_path: str) -> Image.Image:
    """Add logo to top-right corner."""
    if not logo_path or not os.path.exists(logo_path):
        return canvas
    try:
        W, H = canvas.size
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 100
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        pos = (W - logo.width - 40, 35)
        canvas.paste(logo, pos, logo)
    except Exception as e:
        logger.warning(f"Logo paste failed: {e}")
    return canvas


# ── Main Composer ─────────────────────────────────────────
def compose_graphic(
    width: int,
    height: int,
    headline: str,
    tagline: str,
    primary_color: str = "#3B82F6",
    secondary_color: str = "#8B5CF6",
    template_theme: str = "corporate",
    layout_seed: int = 0,
    company_name: str = "",
    logo_path: str = "",
) -> Image.Image:
    """
    Compose a premium marketing graphic — the Python equivalent of the
    Canva MCP's sharp-based image-composer.ts.
    """
    # Pick layout
    layout = LAYOUTS[layout_seed % len(LAYOUTS)]
    logger.info(f"[Composer] Layout: {layout['id']} | Theme: {template_theme} | {width}x{height}")

    # 1. Background
    canvas = _generate_gradient_background(width, height, primary_color, secondary_color, template_theme)

    # 2. Gradient overlay
    accent_rgba = _hex_to_rgba(primary_color)
    canvas = _apply_gradient(canvas, layout["grad_direction"], layout["grad_opacity"], accent_rgba)

    # 3. Text
    canvas = _render_text_block(canvas, headline, tagline, layout, primary_color, company_name)

    # 4. Logo
    if logo_path:
        canvas = _add_logo(canvas, logo_path)

    return canvas


# ── ImageGenerator Class (Pipeline Integration) ───────────
class ImageGenerator:
    """Generates premium static marketing graphics using Pillow composition."""

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

    async def generate_async(self, config: dict) -> dict:
        """
        config expects:
        {
          "graphics_config": { "headline", "tagline", "template_theme", "layout_seed" },
          "graphic_size": "square" | "portrait" | "both"
        }
        """
        graphic_size = config.get("graphic_size", "both")
        gc = config.get("graphics_config", {})

        headline = gc.get("headline", "Premium Campaign.")
        tagline = gc.get("tagline", "Elevate your brand.")
        template_theme = gc.get("template_theme", "corporate")
        layout_seed = gc.get("layout_seed", random.randint(0, 100))

        primary = self.profile.get("brand_primary_color", "#3B82F6")
        secondary = self.profile.get("brand_secondary_color", "#8B5CF6")
        company_name = self.profile.get("company_name", "")

        # Resolve logo
        logo_path = ""
        raw_logo = self.profile.get("logo_url", "")
        if raw_logo and "/outputs/assets/" in raw_logo:
            filename = raw_logo.split("/")[-1].split("?")[0]
            local = os.path.join(self.backend_dir, "data", "outputs", "assets", filename)
            if os.path.exists(local):
                logo_path = local
                logger.info(f"[Image:{self.run_id}] Logo found: {logo_path}")

        self._update_progress(1, 3, "Composing marketing graphics...", f"Theme: {template_theme}")

        results = []

        # Run composition in executor to keep event loop free
        loop = asyncio.get_event_loop()

        if graphic_size in ("square", "both"):
            try:
                sq_path = os.path.join(self.outputs_dir, f"graphic_sq_{self.run_id}.png")
                logger.info(f"[Image:{self.run_id}] Generating square graphic: {sq_path}")
                img = await loop.run_in_executor(None, lambda: compose_graphic(
                    1080, 1080, headline, tagline, primary, secondary,
                    template_theme, layout_seed, company_name, logo_path
                ))
                
                # Save with optimal settings for Photopea compatibility
                img.save(sq_path, "PNG", quality=95, optimize=True)
                
                # Verify the file was created and is valid
                if os.path.exists(sq_path):
                    file_size = os.path.getsize(sq_path)
                    logger.success(f"[Image:{self.run_id}] Square graphic saved: {sq_path} ({file_size/1024:.1f}KB)")
                    results.append(f"/outputs/graphic_sq_{self.run_id}.png")
                else:
                    logger.error(f"[Image:{self.run_id}] Square graphic file not found after save")
            except Exception as e:
                logger.error(f"[Image:{self.run_id}] Square graphic failed: {e}", exc_info=True)

        self._update_progress(2, 3, "Rendering portrait variant...", "")

        if graphic_size in ("portrait", "both"):
            try:
                pt_path = os.path.join(self.outputs_dir, f"graphic_pt_{self.run_id}.png")
                logger.info(f"[Image:{self.run_id}] Generating portrait graphic: {pt_path}")
                img = await loop.run_in_executor(None, lambda: compose_graphic(
                    1080, 1350, headline, tagline, primary, secondary,
                    template_theme, layout_seed + 1, company_name, logo_path
                ))
                
                # Save with optimal settings for Photopea compatibility
                img.save(pt_path, "PNG", quality=95, optimize=True)
                
                # Verify the file was created and is valid
                if os.path.exists(pt_path):
                    file_size = os.path.getsize(pt_path)
                    logger.success(f"[Image:{self.run_id}] Portrait graphic saved: {pt_path} ({file_size/1024:.1f}KB)")
                    results.append(f"/outputs/graphic_pt_{self.run_id}.png")
                else:
                    logger.error(f"[Image:{self.run_id}] Portrait graphic file not found after save")
            except Exception as e:
                logger.error(f"[Image:{self.run_id}] Portrait graphic failed: {e}", exc_info=True)

        self._update_progress(3, 3, "Graphics ready!", f"Generated {len(results)} images.")

        return {
            "type": "graphics",
            "image_urls": results,
        }
