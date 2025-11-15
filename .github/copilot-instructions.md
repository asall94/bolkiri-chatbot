# Copilot Instructions for Bolkiri Chatbot

## Overview

AI-powered customer support chatbot for Bolkiri Vietnamese restaurant chain. Built with 100% RAG/Agentic architecture.

**Tech Stack:**
- Backend: FastAPI (Python 3.12)
- AI: OpenAI GPT-4o-mini + FAISS
- Deployment: Render.com
- CI/CD: GitHub Actions

## Architecture

### Components

1. **Backend**
   - Entry point: `main.py`
   - AI agent: `ai_agent.py` (tool calling + validation)
   - RAG wrapper: `knowledge_base_enriched.py`
   - Search engine: `rag_engine.py` (FAISS)

2. **Frontend**
   - React widget in `frontend/`
   - Chat UI: `static/index.html`, `docs/index.html`

3. **Knowledge Base**
   - Source: `bolkiri_knowledge_industrial_2025.json`
   - Generator: `scraper_industrial_2025.py` (JSON-LD + HTML)
   - FAISS semantic search

4. **Deployment**
   - Platform: Render.com
   - Scripts: `deploy_all.bat`
   - CI/CD: `.github/workflows/auto-scraping.yml` (weekly)

## CRITICAL: Architecture Principles

**Architecture MUST remain 100% RAG/Agentic:**

1. **Single Source of Truth**: Knowledge base (`bolkiri_knowledge_industrial_2025.json`)
   - All data from scraper (restaurants, menu, schedules, links)
   - ZERO hardcoded data in code or prompts

2. **RAG Flow**:
   ```
   Query → RAG Search → Context Retrieval → LLM → Response
   ```
   - Retrieved context = source of truth
   - LLM NEVER contradicts context
   - No hardcoded data in system prompts

3. **Links and URLs**:
   - Injected by scraper (HTML format `<a href="..." target="_blank">`)
   - LLM copies links AS-IS from context
   - NEVER hardcode URLs in prompts

4. **Validation**:
   - `_validate_response()` checks context coherence
   - Auto-detects hallucinations (restaurants, schedules, prices)

5. **Update Flow**:
   ```
   Website Change → Scraper → KB Regen → FAISS Rebuild → Auto-Propagation
   ```
   - No manual code changes needed for data updates

## Development Workflows

### Backend Setup

```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key" > .env
python main.py
```

### Frontend Setup

```bash
cd frontend
npm install && npm start
```

### Testing

Run tests:
```bash
python test_rag.py
python test_multilingual.py
```

### Deployment

See `DEPLOYMENT.md` for Render.com guide.

## Conventions

**Architecture:**
- NEVER hardcode data in prompts/code
- All info from KB via RAG
- Single source of truth: `bolkiri_knowledge_industrial_2025.json`

**KB Updates:**
- Run: `python scraper_industrial_2025.py`
- Auto-rebuild FAISS via `REBUILD_EMBEDDINGS` env var

**Error Handling:**
- Raise `HTTPException` for uninitialized states

**Logging:**
- Text-based: `[OK]`, `[WARN]`, `[ERROR]`
- No emojis (Windows compatibility)

## Integration Points

**OpenAI:**
- Model: `gpt-4o-mini`
- Temperature: 0.1 (deterministic)
- Requires: `OPENAI_API_KEY`

**FAISS:**
- Embedding: `text-embedding-ada-002`
- Index: `IndexFlatIP` (exact search)

**Render.com:**
- Runtime: Python 3.12
- Auto-deploy: GitHub push to `main`

## Key Files and Directories
- `main.py`: Backend entry point.
- `ai_agent.py`: Core AI logic with validation system.
- `knowledge_base_enriched.py`: FAISS RAG wrapper with Bolkiri-specific methods.
- `rag_engine.py`: FAISS semantic search engine.
- `scraper_industrial_2025.py`: Web scraper for KB generation (JSON-LD + HTML parsing).
- `bolkiri_knowledge_industrial_2025.json`: Knowledge base (20 restaurants, ~32 menu items, 19 pages).
- `frontend/`: React-based chat widget.
- `static/index.html` & `docs/index.html`: Chat UIs with favicon.
- `requirements.txt`: Python dependencies.
- `runtime.txt`: Python version for Render (3.12).
- `Procfile`: Render deployment config.
- `.github/workflows/auto-scraping.yml`: Weekly scraping automation (Thursday 2am).

## Notes for AI Agents
- Ensure the `.env` file is correctly configured before running the backend.
- Refer to `README.md` and `docs/` for additional context.
- Follow the project structure and conventions to maintain consistency.
- Be concise, professional, and direct in all interactions.