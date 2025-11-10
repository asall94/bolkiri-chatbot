# Bolkiri Chatbot# Bolkiri Chatbot# Restaurant Chatbot - Bolkiri



Assistant IA pour le restaurant Bolkiri, spécialisé en cuisine vietnamienne.



## ArchitectureChatbot intelligent pour le restaurant Bolkiri, spécialisé en cuisine vietnamienne.AI-powered chatbot for Vietnamese restaurant Bolkiri.



- **Backend**: FastAPI (Python)

- **AI**: OpenAI GPT-4

- **Deployment**: Render.com## Architecture## Architecture

- **Frontend**: React widget



## Fonctionnalités

- **Backend**: FastAPI (Python)- **Backend**: FastAPI (Python)

- Support client 24/7

- Informations sur le menu et recommandations- **Frontend**: React- **Frontend**: React

- Horaires et localisations des restaurants

- Gestion des réservations- **AI**: OpenAI GPT-3.5- **AI**: OpenAI GPT-4

- Base de connaissances enrichie

- **Base de connaissances**: ChromaDB- **Deployment**: Render.com

## Installation Locale

- **Web Scraping**: BeautifulSoup4

### Backend

## Features

```bash

pip install -r requirements.txt## Structure du Projet

```

- 24/7 customer support

Créer un fichier `.env`:

``````- Menu information and recommendations

OPENAI_API_KEY=votre_clé_api

WEBSITE_URL=https://bolkiri.frbackend/          - API FastAPI et logique métier- Reservation inquiries

```

frontend/         - Widget de chat React- Opening hours and location

Démarrer le serveur:

```bashintegration/      - Script d'intégration pour site web- Delivery and takeout information

python main.py

```docs/            - Documentation technique- Allergen information



### Frontend```



```bash## Project Structure

cd frontend

npm install## Fonctionnalités

npm start

``````



## Déploiement- Support client automatisébackend/          - FastAPI server



Le projet est configuré pour Render.com.- Informations sur le menu et recommandationsfrontend/         - React chat widget



Voir `DEPLOYMENT.md` pour les instructions détaillées.- Gestion des horaires et disponibilitésdocs/            - Documentation



## Configuration- Extraction automatique de données du site web```



### Variables d'environnement- Base de connaissances mise à jour dynamiquement



- `OPENAI_API_KEY`: Clé API OpenAI (obligatoire)## Installation

- `WEBSITE_URL`: URL du site (défaut: https://bolkiri.fr)

## Installation

## Scripts

See detailed instructions in `docs/INSTALLATION.md`

- `start_backend.bat`: Démarre le serveur backend

### Backend

## Structure

## Deployment

```

├── main.py              - API FastAPI```bash

├── ai_agent.py          - Agent IA

├── knowledge_base_enriched.py - Base de connaissancescd backendConfigured for one-click deployment on Render.com

├── static/              - Interface chatbot

├── frontend/            - Widget Reactpip install -r requirements.txt

└── docs/                - Documentation```

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
