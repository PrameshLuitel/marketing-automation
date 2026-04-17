# Marketing Department Automation

> 🚀 AI-powered marketing automation platform — scrape, analyze, generate campaigns with **zero cost** using free-tier APIs.

## Architecture

```
Scheduler → Scraping → Storage → Analysis → Agent Council → Creative Output → Dashboard → Notifications
```

**Modules:**
1. **Scraping** — YouTube transcripts, TikTok hashtags, News/RSS feeds
2. **Storage** — SQLite + ChromaDB vector store (all local)
3. **Analysis** — Sentiment, topics (BERTopic), emotions (all local ML models)
4. **Agent Council** — 5 AI agents via Groq/Gemini/Mistral free tiers
5. **Creative Output** — Image gen (Pollinations.ai) + campaign briefs (Markdown/PDF)
6. **Web Dashboard** — React + Vite premium dark-mode UI
7. **Notifications** — Email, Slack, Telegram

## Quick Start

### 1. Clone & Setup Backend
```bash
cd backend
cp .env.example .env
# Edit .env with your free API keys:
#   - Groq: https://console.groq.com
#   - Gemini: https://aistudio.google.com
#   - Mistral: https://console.mistral.ai

python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

### 2. Setup Frontend
```bash
cd frontend
npm install
```

### 3. Run Development
```bash
# Terminal 1 — Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

### 4. Open Dashboard
Visit **http://localhost:5173** — click "Run Pipeline" to start!

## Free Tier Budget

| Provider | Free Limit | Our Usage | Status |
|----------|-----------|-----------|--------|
| Groq | ~14,400 req/day | ~200/day | ✅ |
| Gemini Flash | 100-1,000 req/day | ~50/day | ✅ |
| Mistral | ~1 req/sec | ~100/day | ✅ |
| Pollinations.ai | Unlimited | ~5-10/day | ✅ |
| SQLite + ChromaDB | Local | Unlimited | ✅ |
| BERTopic + Transformers | Local | Unlimited | ✅ |

## Deployment (Free)

### Render.com
```bash
# Just push to GitHub and connect to Render
# render.yaml is already configured
```

### Docker
```bash
# Build frontend first
cd frontend && npm run build && cd ..

# Run with Docker Compose
docker-compose up --build
```

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app + full pipeline
│   ├── config.py             # Settings & env vars
│   ├── scrapers/             # YouTube, TikTok, News scrapers
│   ├── storage/              # SQLite + ChromaDB
│   ├── analysis/             # Sentiment, topics, emotions (local)
│   ├── agents/               # LLM router + 5-agent council
│   ├── creative/             # Image gen + brief generator
│   ├── notifications/        # Email, Slack, Telegram
│   └── scheduler/            # APScheduler daily jobs
├── frontend/
│   └── src/
│       ├── pages/            # Dashboard, Trends, Campaigns, Gallery, Logs, Settings
│       └── components/       # Sidebar, Header
├── Dockerfile
├── docker-compose.yml
├── render.yaml
└── .github/workflows/        # Backup scheduler
```

## License

MIT
