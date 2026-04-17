# 🎨 How to Edit Layered Designs in Photopea

## What You Get

For each design, the system generates **6 files**:

```
design_sq_layered_demo_v1.png              ← Flattened composite (for preview)
design_sq_layered_demo_v1_background.png   ← Background layer
design_sq_layered_demo_v1_products.png     ← Product images layer
design_sq_layered_demo_v1_gradient_overlay.png ← Color grading layer
design_sq_layered_demo_v1_text.png         ← Text layer (headline, tagline)
design_sq_layered_demo_v1_logo.png         ← Company logo layer
```

## Quick Start: 3 Steps to Edit

### Step 1: Open Photopea
Go to: **https://www.photopea.com**

### Step 2: Import Layers
1. **File → Open** → Select the composite PNG
2. **File → Open & Place** → Select each layer PNG one by one
3. **OR** Drag and drop all layer files directly into Photopea

### Step 3: Edit!
Each layer appears separately in the Layers panel (right side). You can:
- 👁️ **Toggle visibility** (eye icon)
- 🔒 **Lock/unlock** layers
- 🎨 **Edit** text, colors, positions
- 🗑️ **Delete** layers you don't need
- 📥 **Import** new images as layers

---

## Detailed Editing Guide

### 🎨 Edit the Background
**Layer**: `design_sq_*_background.png`

**What you can change:**
- Colors (Image → Adjustments → Hue/Saturation)
- Add patterns or textures
- Replace with a different background
- Adjust gradient direction

**Steps:**
1. Select the background layer
2. Use Paint Bucket, Gradient, or Brush tools
3. Or: File → Open new background, drag to replace

---

### 📦 Edit Product Images
**Layer**: `design_sq_*_products.png`

**What you can change:**
- Replace product images
- Resize products (Ctrl/Cmd + T)
- Move products to different positions
- Add/remove drop shadows
- Adjust brightness/contrast

**Steps to replace product:**
1. Hide or delete the products layer
2. File → Open & Place → Select new product image
3. Resize: Ctrl/Cmd + T (Free Transform)
4. Position with Move tool (V)
5. Add shadow: Layer → Layer Style → Drop Shadow

---

### ✏️ Edit Text
**Layer**: `design_sq_*_text.png`

**What you can change:**
- Headline text content
- Tagline text
- Font family and size
- Text color
- Text position

**Steps:**
1. Select the text layer
2. Use Type tool (T) to edit text
3. Change font in top toolbar
4. Adjust size and color
5. Move with Move tool (V)

**Note**: Since text is rasterized in the PNG, you may want to:
- Use the text layer as a guide
- Create new text layers for editing
- Delete old text layer when done

---

### 🏢 Edit Logo
**Layer**: `design_sq_*_logo.png`

**What you can change:**
- Replace with different logo
- Resize logo
- Reposition logo
- Adjust opacity
- Add effects (glow, shadow, etc.)

**Steps:**
1. Select logo layer
2. Replace: File → Open & Place → New logo
3. Resize: Ctrl/Cmd + T
4. Move to desired position

---

### 🌈 Adjust Color Grading
**Layer**: `design_sq_*_gradient_overlay.png`

**What you can change:**
- Blend mode (Normal, Multiply, Overlay, etc.)
- Opacity (transparency)
- Color of gradient
- Remove entirely for cleaner look

**Steps:**
1. Select gradient overlay layer
2. Change blend mode in Layers panel dropdown
3. Adjust opacity slider (top right of Layers panel)
4. Or delete layer to remove effect

---

## Pro Tips

### 💡 Non-Destructive Editing
- **Never delete original layers** - hide them instead (eye icon)
- **Duplicate layers** before making major changes
- **Use adjustment layers** for color changes

### 🎯 Precise Positioning
- Use **Arrow keys** for pixel-perfect movement
- Hold **Shift + Arrow** for 10px jumps
- Use **guides** (drag from rulers) for alignment

### 🔄 Mix & Match Layers
Combine layers from different designs:
1. Open Design A composite
2. Import text layer from Design B
3. Import products from Design C
4. Create unique combinations!

### 💾 Export Options
- **PNG**: Best for web/social media
- **JPG**: Smaller file size
- **PSD**: Save for future editing (File → Save as PSD)

---

## Common Editing Scenarios

### Scenario 1: Client wants different product
```
1. Open composite in Photopea
2. Hide existing products layer (eye icon)
3. File → Open & Place → New product image
4. Resize and position
5. Export as PNG
```

### Scenario 2: A/B test different headlines
```
1. Open design in Photopea
2. Select text layer
3. Duplicate text layer (Ctrl/Cmd + J)
4. Edit text on duplicate
5. Export both versions
```

### Scenario 3: Change brand colors
```
1. Open all layers in Photopea
2. Select background layer
3. Image → Adjustments → Hue/Saturation
4. Adjust to new brand colors
5. Update gradient overlay color
6. Export updated design
```

### Scenario 4: Create multiple formats
```
1. Start with square design layers
2. Resize canvas: Image → Canvas Size
3. Reposition layers for portrait/landscape
4. Export in new format
```

---

## Keyboard Shortcuts

| Action | Windows | Mac |
|--------|---------|-----|
| Free Transform | Ctrl + T | Cmd + T |
| Duplicate Layer | Ctrl + J | Cmd + J |
| Select All | Ctrl + A | Cmd + A |
| Deselect | Ctrl + D | Cmd + D |
| Undo | Ctrl + Z | Cmd + Z |
| Zoom In | Ctrl + + | Cmd + + |
| Zoom Out | Ctrl + - | Cmd + - |
| Move Tool | V | V |
| Type Tool | T | T |
| Brush Tool | B | B |

---

## Troubleshooting

### Q: Layers don't align properly?
**A**: Make sure all layers are the same dimensions (1080x1080 or 1080x1350)

### Q: Text looks pixelated when edited?
**A**: The text is rasterized in PNG. Create new text layer with Type tool for crisp text.

### Q: Can I get actual editable text?
**A**: For fully editable text, you need PSD format. Request PSD generation feature or recreate text in Photopea.

### Q: How do I save my edits?
**A**: File → Save as PSD (keeps layers) or File → Export as PNG/JPG (flattened)

---

## Next Steps

1. ✅ Try editing a simple design first
2. ✅ Experiment with layer visibility
3. ✅ Practice replacing product images
4. ✅ Try different text fonts and colors
5. ✅ Create your own design variations

**Happy Editing! 🎨✨**
