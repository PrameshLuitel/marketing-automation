# Layered Design System for Photopea

## Overview
The enhanced image generator now creates **individual layer files** that can be opened and edited separately in Photopea.

## How It Works

### Generated Files
For each design variation, the system creates:
- `design_sq_RUNID_v1.png` - Flattened preview (for gallery)
- `design_sq_RUNID_v1_background.png` - Background layer
- `design_sq_RUNID_v1_products.png` - Product images layer (if any)
- `design_sq_RUNID_v1_gradient_overlay.png` - Gradient overlay layer
- `design_sq_RUNID_v1_text.png` - Text layer (headline, tagline, company name)
- `design_sq_RUNID_v1_logo.png` - Company logo layer (if available)

### Editing in Photopea

1. **Open Photopea**: Go to https://www.photopea.com
2. **Import Base Image**: File → Open → Select the flattened PNG
3. **Add Layers as Separate Files**: 
   - File → Open & Place → Select layer PNGs
   - Or drag and drop layer files directly
4. **Edit Each Layer**:
   - **Background**: Change colors, gradients, patterns
   - **Products**: Resize, move, replace product images
   - **Text**: Edit text content, font, size, color
   - **Logo**: Replace or reposition logo
   - **Gradient**: Adjust opacity, blend modes

### Layer Order (Bottom to Top)
```
1. Background (base layer)
2. Products (product images with shadows)
3. Gradient Overlay (color grading)
4. Text (headline, tagline, company name)
5. Logo (company branding)
```

## Benefits

✅ **Fully Editable**: Every element can be modified independently
✅ **Non-Destructive**: Original layers remain intact
✅ **Flexible**: Mix and match layers from different designs
✅ **Professional**: Maintain design consistency across campaigns
✅ **No Dependencies**: Works with standard PNG files

## Example Workflow

### Scenario: Client wants to change product image but keep everything else

1. Open the flattened design in Photopea
2. Hide or delete the existing "products" layer
3. Import new product image: File → Open & Place
4. Position and resize as needed
5. Export: File → Export as → PNG

### Scenario: A/B test different headlines

1. Open design in Photopea
2. Select the "text" layer
3. Edit the headline text
4. Export as new version
5. Repeat for multiple variations

## Technical Details

### Layer Generation
- Each layer is a transparent PNG (RGBA)
- Layers maintain original positioning
- Drop shadows are included in product layer
- Text has transparent background for easy editing

### File Naming Convention
```
design_{size}_{run_id}_v{variation}.png          # Flattened
design_{size}_{run_id}_v{variation}_{layer}.png  # Individual layers
```

Sizes: `sq` (1080x1080), `pt` (1080x1350)
Layers: `background`, `products`, `gradient_overlay`, `text`, `logo`

## Future Enhancement: PSD Files

To generate actual PSD files with native layers:
1. Install: `pip install psd-tools`
2. Use PSDTools library to create layered PSD
3. Photopea opens PSD files with layers intact

However, individual PNG layers provide the same editing capability with better compatibility.
