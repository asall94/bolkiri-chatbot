# Copilot Instructions for Bolkiri Chatbot

## Overview
Bolkiri Chatbot is an AI-powered assistant for the Vietnamese restaurant Bolkiri. It provides customer support, menu recommendations, reservation management, and more. The project is built with the following technologies:

- **Backend**: FastAPI (Python)
- **Frontend**: React widget
- **AI**: OpenAI GPT-4
- **Database**: ChromaDB for knowledge base
- **Deployment**: Render.com

## Architecture
The project is divided into the following components:

1. **Backend**:
   - Located in the root directory.
   - Main entry point: `main.py`.
   - Core logic: `ai_agent.py` (AI agent implementation), `knowledge_base_enriched.py` (knowledge base management).
   - REST API built with FastAPI.

2. **Frontend**:
   - Located in the `frontend/` directory.
   - React-based chat widget for user interaction.

3. **Knowledge Base**:
   - JSON files like `bolkiri_knowledge_complete.json` store structured data.
   - Managed and updated dynamically by scripts like `knowledge_base_enriched.py`.

4. **Deployment**:
   - Configured for Render.com.
   - Deployment scripts: `deploy_all.bat`, `deploy_to_github.bat`.

## Developer Workflows

### Setting Up the Backend
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=votre_clé_api
   WEBSITE_URL=https://bolkiri.fr
   ```
3. Start the backend server:
   ```bash
   python main.py
   ```

### Setting Up the Frontend
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the frontend server:
   ```bash
   npm start
   ```

### Running Tests
- Backend tests are located in files like `test_rag.py` and `test_multilingual.py`.
- Run tests using:
  ```bash
  python -m unittest discover
  ```

### Deployment
- Follow instructions in `docs/DEPLOYMENT.md` for deploying to Render.com.

## Project-Specific Conventions
- **Knowledge Base Updates**:
  - Use `regenerate_kb.bat` to refresh the knowledge base.
- **Error Handling**:
  - The AI agent raises `HTTPException` for uninitialized states (e.g., `agent is None`).
- **Logging**:
  - Use `print` statements for debugging during development.

## Integration Points
- **OpenAI GPT-4**:
  - Integrated via `ai_agent.py`.
  - Requires `OPENAI_API_KEY`.
- **ChromaDB**:
  - Used for storing and querying the knowledge base.
- **Render.com**:
  - Deployment platform.

## Key Files and Directories
- `main.py`: Backend entry point.
- `ai_agent.py`: Core AI logic.
- `knowledge_base_enriched.py`: Knowledge base management.
- `frontend/`: React-based frontend.
- `docs/`: Documentation, including deployment instructions.
- `requirements.txt`: Python dependencies.
- `start_backend.bat`: Script to start the backend server.
- `deploy_all.bat`: Script for deploying the entire application.
- `regenerate_kb.bat`: Script to update the knowledge base.

## Notes for AI Agents
- Ensure the `.env` file is correctly configured before running the backend.
- Refer to `README.md` and `docs/` for additional context.
- Follow the project structure and conventions to maintain consistency.
- Be concise, professional, and direct in all interactions.