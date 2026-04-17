# Quick Start Guide - Testing Image Design & Photopea

## 🚀 Quick Test (5 minutes)

### Step 1: Verify Backend is Running
```bash
cd backend
python main.py
```
You should see: `Platform started successfully`

### Step 2: Verify Frontend is Running
```bash
cd frontend
npm run dev
```
You should see: `Local: http://localhost:5175/`

### Step 3: Test Image Generation
```bash
# From project root
python test_image_generation.py
```
This will generate test images in `backend/data/outputs/`

### Step 4: Open the App
1. Navigate to: http://localhost:5175/images
2. You should see the Image Studio page
3. If you have generated images, they will appear in a grid

### Step 5: Test Preview Modal
1. Click on any image in the gallery
2. A beautiful fullscreen preview should appear
3. You'll see:
   - Image title and date
   - Download button
   - "Edit in Photopea" button

### Step 6: Test Photopea Editor
1. Click "Edit in Photopea" from the preview
2. Wait for Photopea to load (3-5 seconds first time)
3. The status indicator should change from "Loading" → "Ready"
4. Your image should appear in the Photopea canvas
5. Try editing (add text, adjust colors, etc.)
6. Click "Save & Download"
   - The edited image will download to your computer
   - It will also save to the backend

## 🎨 What You'll See

### Gallery Page
```
┌─────────────────────────────────────────┐
│  Image Studio                           │
│  Professional layer-based marketing     │
│  asset studio                           │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐            │
│  │ IMG 1│ │ IMG 2│ │ IMG 3│            │
│  └──────┘ └──────┘ └──────┘            │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐            │
│  │ IMG 4│ │ IMG 5│ │ IMG 6│            │
│  └──────┘ └──────┘ └──────┘            │
└─────────────────────────────────────────┘
```

### Preview Modal
```
┌─────────────────────────────────────────┐
│  Marketing Graphic Title          [X]   │
│  April 17, 2026                         │
│                                         │
│         ┌───────────────┐               │
│         │               │               │
│         │   IMAGE       │               │
│         │   PREVIEW     │               │
│         │               │               │
│         └───────────────┘               │
│                                         │
│    [Download]  [Edit in Photopea]       │
└─────────────────────────────────────────┘
```

### Photopea Editor
```
┌─────────────────────────────────────────┐
│ [X] 🎨 Graphic Title  ● Ready [Save]    │
├─────────────────────────────────────────┤
│                                         │
│           PHOTOPEA EDITOR               │
│                                         │
│      Your image loaded here             │
│      Full Photopea interface            │
│      with all tools                     │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

## ✅ Success Indicators

### Image Generation Works
- ✅ Test script completes without errors
- ✅ Images appear in `backend/data/outputs/`
- ✅ File sizes are 100KB+ (not empty)

### Preview Works
- ✅ Clicking image opens modal
- ✅ Image displays clearly
- ✅ Buttons are visible and clickable
- ✅ Smooth animations

### Photopea Works
- ✅ Photopea loads in iframe
- ✅ Status shows "Ready" (green)
- ✅ Image appears in canvas
- ✅ Can interact with Photopea tools
- ✅ Save button works
- ✅ Download triggers

## 🐛 Common Issues & Fixes

### Issue: "Failed to load image"
**Fix:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check image exists: `ls backend/data/outputs/`
3. Click the "Retry" button
4. Check browser console for errors

### Issue: Photopea shows blank
**Fix:**
1. Wait 5-10 seconds (first load is slow)
2. Check internet connection (Photopea loads from CDN)
3. Try refreshing the page
4. Check browser console for errors

### Issue: Save button doesn't work
**Fix:**
1. Make sure status shows "Ready" (not "Loading")
2. Make sure you've made at least one change
3. Check browser console for errors
4. Try the download button instead

### Issue: Images not showing in gallery
**Fix:**
1. Run the test script: `python test_image_generation.py`
2. Check database has assets: Query the CreativeAsset table
3. Refresh the gallery page
4. Check browser console for API errors

## 🎯 Next Steps

1. **Generate Real Images**: Run a full pipeline from the Dashboard
2. **Customize Company Profile**: Add your brand colors and logo in Settings
3. **Try Different Themes**: Generate images with different themes
4. **Edit in Photopea**: Make professional edits to your designs
5. **Download & Use**: Use the images in your marketing campaigns

## 📝 Notes

- **First Photopea Load**: Takes 3-5 seconds (caches after that)
- **Image Format**: All images are PNG with RGBA (Photopea compatible)
- **Resolution**: 1080x1080 (square) and 1080x1350 (portrait)
- **Browser**: Works best in Chrome/Edge, also works in Firefox/Safari

## 🆘 Need Help?

Check the detailed documentation:
- `IMAGE_DESIGN_IMPROVEMENTS.md` - Full feature documentation
- `backend/creative/image_gen.py` - Image generation code
- `frontend/src/components/PhotopeaEditor.jsx` - Photopea integration
- `frontend/src/pages/Gallery.jsx` - Gallery and preview modal

---

**Enjoy your improved image design experience! 🎨✨**
