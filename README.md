# Bolkiri Chatbot# Restaurant Chatbot - Bolkiri



Chatbot intelligent pour le restaurant Bolkiri, spécialisé en cuisine vietnamienne.AI-powered chatbot for Vietnamese restaurant Bolkiri.



## Architecture## Architecture



- **Backend**: FastAPI (Python)- **Backend**: FastAPI (Python)

- **Frontend**: React- **Frontend**: React

- **AI**: OpenAI GPT-3.5- **AI**: OpenAI GPT-4

- **Base de connaissances**: ChromaDB- **Deployment**: Render.com

- **Web Scraping**: BeautifulSoup4

## Features

## Structure du Projet

- 24/7 customer support

```- Menu information and recommendations

backend/          - API FastAPI et logique métier- Reservation inquiries

frontend/         - Widget de chat React- Opening hours and location

integration/      - Script d'intégration pour site web- Delivery and takeout information

docs/            - Documentation technique- Allergen information

```

## Project Structure

## Fonctionnalités

```

- Support client automatisébackend/          - FastAPI server

- Informations sur le menu et recommandationsfrontend/         - React chat widget

- Gestion des horaires et disponibilitésdocs/            - Documentation

- Extraction automatique de données du site web```

- Base de connaissances mise à jour dynamiquement

## Installation

## Installation

See detailed instructions in `docs/INSTALLATION.md`

### Backend

## Deployment

```bash

cd backendConfigured for one-click deployment on Render.com

pip install -r requirements.txt
```

Créer un fichier `.env`:
```
OPENAI_API_KEY=votre_clé_api
WEBSITE_URL=https://bolkiri.fr
```

Démarrer le serveur:
```bash
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

## Déploiement

Le projet est configuré pour un déploiement sur Render.com.

Voir `docs/DEPLOYMENT.md` pour les instructions détaillées.

## Configuration

### Variables d'environnement

- `OPENAI_API_KEY`: Clé API OpenAI (obligatoire)
- `WEBSITE_URL`: URL du site à scraper (défaut: https://bolkiri.fr)

## Scripts de Démarrage

- `start_backend.bat`: Démarre le serveur backend
- `start_frontend.bat`: Démarre l'interface frontend

## Support

Pour toute question ou problème, consultez la documentation dans le dossier `docs/`.
