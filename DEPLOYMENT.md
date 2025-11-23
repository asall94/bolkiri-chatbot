# Deployment Guide

Production deployment on Render.com (free tier sufficient).

## Environment Variables

Set these in Render dashboard:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `WEBSITE_URL` | Bolkiri website URL | No (default: bolkiri.fr) |
| `REBUILD_EMBEDDINGS` | Force FAISS rebuild on deploy | No (default: true) |

## Deployment Steps

1. **Connect GitHub** → Render auto-detects `runtime.txt` (Python 3.12) + `Procfile`
2. **Set env var** → `OPENAI_API_KEY` in dashboard
3. **Deploy** → Auto-deploys on push to `main`, rebuilds embeddings on first boot

## CI/CD & Health

- **Auto-scraping:** GitHub Actions weekly (Thursday 2am UTC) → scrape → commit → deploy
- **Health check:** `GET /health` returns `{"status": "healthy", "agent": "ready"}`
- **Scaling:** Free tier 1 instance (sleeps after 15min), paid tier auto-scale 1-10

## Troubleshooting

| Issue | Solution |
|-------|----------|
| FAISS import error | Verify `faiss-cpu` in `requirements.txt` |
| Embeddings missing | Set `REBUILD_EMBEDDINGS=true` |
| Cold start (30-60s) | Free tier sleeps after 15min inactivity |
| OpenAI rate limit | Upgrade to paid tier or reduce traffic |

## Production URLs

- **API**: `https://bolkiri-chatbot.onrender.com`
- **Health**: `https://bolkiri-chatbot.onrender.com/health`
- **Demo**: `https://asall94.github.io/bolkiri-chatbot/` (GitHub Pages: Settings → Pages → `/docs` folder)

## Monitoring

Render dashboard: response times, error rates, memory usage, deploy logs
