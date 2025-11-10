# Deployment - Quick Start

## Option 1: Automated Script (Windows)

Exécutez `deploy_to_github.bat` et suivez les instructions.

## Option 2: Manual Deployment

### 1. Push to GitHub

```bash
cd backend
git init
git add .
git commit -m "Initial commit - Bolkiri AI Agent"
git remote add origin https://github.com/YOUR_USERNAME/bolkiri-chatbot.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render

1. Go to https://render.com
2. New + → Web Service
3. Connect GitHub repository
4. Configuration:
   - **Name**: bolkiri-chatbot
   - **Region**: Frankfurt (EU Central)
   - **Branch**: main
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

5. Environment Variables:
   - `OPENAI_API_KEY`: your_openai_key_here

6. Click "Create Web Service"

### 3. Verify Deployment

Once deployed, test:

```bash
curl https://YOUR_APP.onrender.com/health
```

Your API URL will be: `https://YOUR_APP.onrender.com`

## Update test_chatbot.html

Replace `http://localhost:8000` with your Render URL:

```javascript
const API_URL = 'https://YOUR_APP.onrender.com';
```

Deploy `test_chatbot.html` on:
- GitHub Pages
- Netlify
- Vercel

Done.
