# Deployment Guide

Production deployment on Render.com (free tier sufficient).

## Environment Variables

Set in Render dashboard: `OPENAI_API_KEY=sk-your-key`

## Deployment Steps

1. **Connect GitHub** → Render auto-detects `runtime.txt` (Python 3.12) + `Procfile`
2. **Set env var** → `OPENAI_API_KEY` in dashboard
3. **Deploy** → Auto-deploys on push to `main`, rebuilds embeddings on first boot

## CI/CD & Health

- **Auto-scraping:** GitHub Actions weekly (Thursday 2am UTC) → scrape → commit → deploy
- **Health check:** `GET /health` returns `{"status": "healthy", "agent": "ready"}`
- **Uptime:** Free tier kept alive 24/7 via UptimeRobot (no cold starts)
- **Scaling:** Paid tier auto-scale 1-10 instances

## Troubleshooting

| Issue | Solution |
|-------|----------|
| FAISS import error | Verify `faiss-cpu` in `requirements.txt` |
| Embeddings missing | Set `REBUILD_EMBEDDINGS=true` |
| OpenAI rate limit | Upgrade to paid tier or reduce traffic |
| High latency | Check UptimeRobot pings (should be <5s interval) |

## Production URLs

- **API**: `https://bolkiri-chatbot.onrender.com`
- **Health**: `https://bolkiri-chatbot.onrender.com/health`
- **Demo**: `https://asall94.github.io/bolkiri-chatbot/` (GitHub Pages: Settings → Pages → `/docs` folder)

## Monitoring

Render dashboard: response times, error rates, memory usage, deploy logs
