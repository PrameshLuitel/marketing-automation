# Marketing Automation Platform

A full-stack AI-powered marketing automation platform with design studio, video templates, and campaign management.

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Video Renderer
```bash
cd video-renderer
npm install
npm run build
```

## 📦 Pushing Updates to GitHub

### Option 1: Using the quick push script
```bash
./push.sh "Your commit message here"
```

### Option 2: Manual git commands
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

### Option 3: Pull latest changes (if working on multiple machines)
```bash
git pull origin main
```

## 🔐 Repository
- **URL**: https://github.com/PrameshLuitel/marketing-automation
- **Visibility**: Private
- **Branch**: main

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints
│   ├── agents/             # AI agents
│   ├── creative/           # Image/video generation
│   ├── scripts/            # Database seed scripts
│   ├── storage/            # Database models
│   └── main.py             # FastAPI app
├── frontend/               # React + Vite frontend
│   └── src/
│       ├── components/     # Reusable components
│       ├── pages/          # Page components
│       └── utils/          # API client, helpers
├── video-renderer/         # Remotion video templates
│   └── src/
│       ├── engines/        # Video template engines
│       └── Root.tsx        # Composition registry
└── push.sh                 # Quick push script
```

## ✨ Features

### Design Studio
- **Image Studio**: Template-based image design with Photopea integration
- **Video Studio**: 12+ professional video templates
- **Pipeline Configurator**: Visual preview of output before rendering

### Video Templates
1. CountdownPromo - Animated countdown for promotions
2. QuoteCard - Elegant quote displays
3. MinimalClean - Clean, minimal aesthetic
4. EventAnnouncement - Bold event announcements
5. StatsCounter - Animated statistics
6. BeforeAfter - Transformation comparisons
7. SocialMediaAd - TikTok/Reels style ads
8. Testimonial - Customer reviews
9. ProductLaunch - Product launch videos
10. KineticTypography - Bold text animations
11. PhotoSlideshow - Photo carousels
12. DataVisualization - Animated charts

### Campaign Management
- AI-generated campaign briefs
- Approval workflow
- Automated pipeline execution
- Multi-channel notifications

## 🛠 Tech Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Frontend**: React 18, Vite, Framer Motion
- **Video**: Remotion (React video creation)
- **Database**: SQLite (async)
- **AI**: OpenRouter LLM integration, BERTopic, ChromaDB
- **Image Generation**: PIL/Pillow with layered design system

## 📝 Database Seeds

Run these scripts to populate the database:
```bash
# Add video templates
python backend/scripts/add_video_templates.py

# Add image templates
python backend/scripts/generate_templates.py

# Add background templates
python backend/scripts/generate_backgrounds.py
```

## 🔑 Environment Variables

Create `backend/.env`:
```env
OPENROUTER_API_KEY=your_key_here
DATABASE_URL=sqlite+aiosqlite:///./data/marketing.db
# ... other variables
```

## 📄 License

Private repository - All rights reserved
