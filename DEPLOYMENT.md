# Deployment Guide

Production deployment on Render.com (free tier sufficient).

## Environment Variables

Set in Render dashboard: `OPENAI_API_KEY=sk-your-key`

## Deployment Steps

1. **Connect GitHub** → Render auto-detects `runtime.txt` (Python 3.12) and `Procfile`
2. **Configure environment** → Set `OPENAI_API_KEY` in Render dashboard
3. **Deploy** → Auto-deploys on push to `main` branch, rebuilds FAISS index on first boot (2-3 min)

## CI/CD & Health

- **Auto-scraping:** GitHub Actions weekly (Thursday 2am UTC) → scrape → commit → deploy
- **Health check:** `GET /health` returns `{"status": "healthy", "agent": "ready"}`
- **Uptime:** Free tier kept alive 24/7 via UptimeRobot (no cold starts)
- **Scaling:** Paid tier auto-scale 1-10 instances

## Troubleshooting

| Issue | Solution |
|-------|----------|
| FAISS import error | Requires Python 3.12 x86_64 (faiss-cpu incompatible with ARM/M1 chips) |
| Embeddings missing | First deploy auto-rebuilds embeddings (wait 2-3 min for FAISS index creation) |
| OpenAI rate limit | Upgrade OpenAI tier or implement rate limiting middleware |
| High latency (>2s) | UptimeRobot configured for 5-min intervals - verify pings active at uptimerobot.com |

## Production URLs

- **API**: `https://bolkiri-chatbot.onrender.com`
- **Health**: `https://bolkiri-chatbot.onrender.com/health`
- **Demo**: `https://asall94.github.io/bolkiri-chatbot/` (GitHub Pages: Settings → Pages → `/docs` folder)

## Monitoring

Render dashboard: response times, error rates, memory usage, deploy logs
