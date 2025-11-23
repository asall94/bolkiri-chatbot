# Deployment Guide

Production deployment on Render.com.

## Prerequisites

- Render.com account
- OpenAI API key
- GitHub repository

## Configuration Files

### `runtime.txt`
```
python-3.12.0
```

### `Procfile`
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### `requirements.txt`
FastAPI, OpenAI, FAISS, etc.

## Environment Variables

Set these in Render dashboard:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `WEBSITE_URL` | Bolkiri website URL | No (default: bolkiri.fr) |
| `REBUILD_EMBEDDINGS` | Force FAISS rebuild on deploy | No (default: true) |

## Deployment Steps

### 1. Create Web Service

- Connect GitHub repository
- Runtime: Python 3.12
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2. Environment Variables

Set `OPENAI_API_KEY` in Render dashboard.

### 3. Auto-Deploy

Auto-deploys on push to `main`.

## CI/CD

### Weekly KB Update

GitHub Actions (`.github/workflows/auto-scraping.yml`):
- Every Thursday 2am UTC
- Scrapes website
- Commits KB updates
- Triggers auto-deploy

## Health Checks

`GET /health` returns `{"status": "healthy", "agent": "ready"}`

## Scaling

- Free tier: 1 instance (sleeps after 15min)
- Paid tier: Auto-scale 1-10 instances

## Troubleshooting

**FAISS Import Error:** Check `faiss-cpu` in `requirements.txt`

**Embeddings Cache Missing:** Set `REBUILD_EMBEDDINGS=true`

**Cold Start Delay:** Free tier sleeps after 15min (first request: 30-60s)

## Production URLs

- **API**: `https://bolkiri-chatbot.onrender.com`
- **Health Check**: `https://bolkiri-chatbot.onrender.com/health`
- **Chat Demo**: `https://asall94.github.io/bolkiri-chatbot/`

## GitHub Pages Setup

Publish demo at `https://asall94.github.io/bolkiri-chatbot/`:

1. **Enable:** Settings → Pages → Deploy from `main` → `/docs` folder
2. **Verify:** `docs/index.html` + `docs/logo_bolkiri.png`
3. **Access:** Wait 1-2 min, then visit URL

**Benefits:** Professional URL, free hosting, auto-deploy, custom domain support

## Monitoring

Render dashboard: response times, error rates, memory usage, deploy logs
