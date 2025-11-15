# Deployment Guide

Production deployment configuration for Bolkiri Chatbot on Render.com.

## Prerequisites

- Render.com account
- OpenAI API key
- GitHub repository (for auto-deploy)

## Configuration Files

### `runtime.txt`
```
python-3.12.0
```
Specifies Python version for Render.

### `Procfile`
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```
Defines web service startup command.

### `requirements.txt`
Production dependencies (FastAPI, OpenAI, FAISS, etc.)

## Environment Variables

Set these in Render dashboard:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes |
| `WEBSITE_URL` | Bolkiri website URL | No (default: bolkiri.fr) |
| `REBUILD_EMBEDDINGS` | Force FAISS rebuild on deploy | No (default: true) |

## Deployment Steps

### 1. Create Web Service on Render

- Connect GitHub repository
- Select Python 3.12 runtime
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2. Set Environment Variables

Add `OPENAI_API_KEY` in Render dashboard.

### 3. Auto-Deploy

Render auto-deploys on git push to `main` branch.

## CI/CD

### Weekly Knowledge Base Update

GitHub Actions workflow (`.github/workflows/auto-scraping.yml`):
- Runs every Thursday at 2am UTC
- Scrapes website for updates
- Commits updated KB to repo
- Triggers auto-deploy on Render

## Health Checks

- **Endpoint**: `GET /health`
- **Expected**: `{"status": "healthy", "agent": "ready"}`

## Scaling

Render auto-scales based on traffic:
- Free tier: 1 instance (sleeps after inactivity)
- Paid tier: Auto-scale 1-10 instances

## Troubleshooting

### FAISS Import Error
Ensure `faiss-cpu` is in `requirements.txt`.

### Embeddings Cache Missing
Set `REBUILD_EMBEDDINGS=true` to force regeneration on deploy.

### Cold Start Delay
Free tier instances sleep after 15min inactivity. First request may take 30-60s.

## Production URLs

- **API**: `https://bolkiri-chatbot.onrender.com`
- **Health Check**: `https://bolkiri-chatbot.onrender.com/health`
- **Chat Demo**: `https://asall94.github.io/bolkiri-chatbot/`

## GitHub Pages Setup

To publish the demo at `https://asall94.github.io/bolkiri-chatbot/`:

1. **Enable GitHub Pages:**
   - Go to repo Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` → `/docs` folder
   - Save

2. **Verify `docs/index.html`:**
   - Must be at root of `/docs` folder
   - Favicon: `docs/logo_bolkiri.png`

3. **Access URL:**
   - Wait 1-2 minutes after enabling
   - Visit: `https://asall94.github.io/bolkiri-chatbot/`

**Benefits:**
- Professional URL (no `.onrender.com` suffix)
- Free static hosting
- Auto-deploy on push to `main`
- Custom domain support (optional)

## Monitoring

Check Render dashboard for:
- Response times
- Error rates
- Memory usage
- Deploy logs
