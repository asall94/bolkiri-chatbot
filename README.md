# Bolkiri Chatbot

Assistant IA pour le restaurant Bolkiri, spécialisé en cuisine vietnamienne.

## Architecture

Bolkiri Chatbot est une application composée des éléments suivants :

- **Backend** : FastAPI (Python)
- **Frontend** : Widget React
- **AI** : OpenAI GPT-4
- **Base de données** : ChromaDB pour la gestion des connaissances
- **Déploiement** : Render.com

## Fonctionnalités

- Support client 24/7
- Informations sur le menu et recommandations
- Gestion des horaires et localisations des restaurants
- Gestion des réservations
- Informations sur les allergènes 
- Base de connaissances enrichie et mise à jour dynamique

## Installation Locale

### Backend

1. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
2. Créer un fichier `.env` avec les variables suivantes :
   ```
   OPENAI_API_KEY=votre_clé_api
   WEBSITE_URL=https://bolkiri.fr
   ```
3. Démarrer le serveur backend :
   ```bash
   python main.py
   ```

### Frontend

1. Naviguer dans le dossier `frontend` :
   ```bash
   cd frontend
   ```
2. Installer les dépendances :
   ```bash
   npm install
   ```
3. Démarrer le serveur frontend :
   ```bash
   npm start
   ```

## Déploiement

Le projet est configuré pour un déploiement sur Render.com. Consultez `docs/DEPLOYMENT.md` pour des instructions détaillées.

## Configuration

### Variables d'environnement

- `OPENAI_API_KEY` : Clé API OpenAI (obligatoire)
- `WEBSITE_URL` : URL du site à scraper (par défaut : https://bolkiri.fr)

## Scripts Utiles

- `start_backend.bat` : Démarre le serveur backend
- `deploy_all.bat` : Script pour déployer l'application complète
- `regenerate_kb.bat` : Met à jour la base de connaissances

## Support

Pour toute question ou problème, consultez la documentation dans le dossier `docs/`.
