# Bolkiri AI Agent - Deployment Guide

## Déploiement sur Render

### Étape 1: Préparer le repository

1. Créer un repository GitHub (public ou privé)
2. Pousser le dossier `backend/` dans le repository

```bash
cd backend
git init
git add .
git commit -m "Initial commit"
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

### Étape 2: Configurer Render

1. Connectez-vous sur https://render.com
2. Cliquez sur "New +" → "Web Service"
3. Connectez votre repository GitHub
4. Configuration:

```
Name: bolkiri-chatbot
Region: Frankfurt (EU Central)
Branch: main
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
Instance Type: Free
```

### Étape 3: Variables d'environnement

Dans "Environment Variables", ajoutez:

```
OPENAI_API_KEY=<votre_clé_openai>
WEBSITE_URL=https://bolkiri.fr
PYTHON_VERSION=3.12.0
```

### Étape 4: Déployer

1. Cliquez sur "Create Web Service"
2. Render va automatiquement:
   - Installer les dépendances
   - Démarrer l'application
   - Générer une URL HTTPS

### Étape 5: Tester

Votre API sera disponible à: `https://bolkiri-chatbot.onrender.com`

Test endpoint:
```bash
curl https://bolkiri-chatbot.onrender.com/health
```

Test chat:
```bash
curl -X POST https://bolkiri-chatbot.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Bonjour"}'
```

### Notes importantes

- Le plan gratuit met le service en veille après 15 min d'inactivité
- Premier appel après veille: ~30-60 secondes de délai
- Pour production: passer au plan payant (7$/mois)

### Fichiers de configuration créés

- `runtime.txt` - Version Python
- `Procfile` - Commande de démarrage
- `render.yaml` - Configuration Render (optionnel)
- `requirements.txt` - Dépendances Python
