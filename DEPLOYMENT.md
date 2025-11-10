# Déploiement sur Render# Bolkiri AI Agent - Deployment Guide



## Prérequis## Déploiement sur Render



- Compte GitHub### Étape 1: Préparer le repository

- Compte Render.com

- Clé API OpenAI1. Créer un repository GitHub (public ou privé)

2. Pousser le dossier `backend/` dans le repository

## Étapes

```bash

### 1. Push sur GitHubcd backend

git init

```bashgit add .

git add .git commit -m "Initial commit"

git commit -m "Initial commit"git remote add origin <YOUR_GITHUB_REPO_URL>

git push origin maingit push -u origin main

``````



### 2. Configuration Render### Étape 2: Configurer Render



1. Aller sur https://render.com1. Connectez-vous sur https://render.com

2. Cliquer sur "New +" → "Web Service"2. Cliquez sur "New +" → "Web Service"

3. Connecter le repository GitHub3. Connectez votre repository GitHub

4. Configuration:4. Configuration:



``````

Name: bolkiri-chatbotName: bolkiri-chatbot

Region: Frankfurt (EU Central)Region: Frankfurt (EU Central)

Branch: mainBranch: main

Runtime: Python 3Root Directory: backend

Build Command: pip install -r requirements.txtRuntime: Python 3

Start Command: uvicorn main:app --host 0.0.0.0 --port $PORTBuild Command: pip install -r requirements.txt

Instance Type: FreeStart Command: uvicorn main:app --host 0.0.0.0 --port $PORT

```Instance Type: Free

```

### 3. Variables d'environnement

### Étape 3: Variables d'environnement

Ajouter dans "Environment Variables":

Dans "Environment Variables", ajoutez:

```

OPENAI_API_KEY=votre_clé_openai```

WEBSITE_URL=https://bolkiri.frOPENAI_API_KEY=<votre_clé_openai>

PYTHON_VERSION=3.12.0WEBSITE_URL=https://bolkiri.fr

```PYTHON_VERSION=3.12.0

```

### 4. Déployer

### Étape 4: Déployer

Cliquer sur "Create Web Service". Render va automatiquement:

- Installer les dépendances1. Cliquez sur "Create Web Service"

- Démarrer l'application2. Render va automatiquement:

- Générer une URL HTTPS   - Installer les dépendances

   - Démarrer l'application

### 5. Tester   - Générer une URL HTTPS



API disponible à: `https://bolkiri-chatbot.onrender.com`### Étape 5: Tester



Test:Votre API sera disponible à: `https://bolkiri-chatbot.onrender.com`

```bash

curl https://bolkiri-chatbot.onrender.com/healthTest endpoint:

``````bash

curl https://bolkiri-chatbot.onrender.com/health

## Notes```



- Plan gratuit: service en veille après 15 min d'inactivitéTest chat:

- Premier appel après veille: 30-60 secondes```bash

- Production: plan payant recommandé (7$/mois)curl -X POST https://bolkiri-chatbot.onrender.com/chat \

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
