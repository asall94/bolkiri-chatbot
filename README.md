# Bolkiri Chatbot - AI-Powered Customer Support

Production-ready AI assistant for Bolkiri Vietnamese restaurant chain, built with RAG architecture and agentic AI patterns.

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **AI**: OpenAI GPT-4o-mini + FAISS semantic search
- **RAG**: Custom retrieval-augmented generation pipeline
- **KB**: Automated web scraping (BeautifulSoup, JSON-LD Schema.org)
- **Deployment**: Render.com with auto-scaling
- **CI/CD**: GitHub Actions (weekly KB updates)

## Key Features

- **100% RAG/Agentic Architecture**: Zero hardcoded data, single source of truth
- **Multilingual Support**: Auto-detects French/Vietnamese/English
- **Hallucination Prevention**: Built-in response validator (4 validation types)
- **Semantic Search**: FAISS vector similarity for context retrieval
- **Auto-Refresh KB**: Weekly scraping + embeddings rebuild
- **Production Scale**: 20 restaurants, 32 menu items, 19 pages indexed

## Quick Start

### Live Demo

**[Try the chatbot here →](https://asall94.github.io/bolkiri-chatbot/)**

### Backend

```bash
pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key" > .env
python main.py
```

### Frontend

```bash
cd frontend
npm install && npm start
```

## Architecture Highlights

**RAG Flow:**
```
User Query → Semantic Search (FAISS) → Context Retrieval → LLM → Validated Response
```

**Key Components:**
- `ai_agent.py`: Agentic AI with tool calling + validation
- `rag_engine.py`: FAISS semantic search engine
- `scraper_industrial_2025.py`: JSON-LD + HTML parser
- `knowledge_base_enriched.py`: RAG wrapper with domain methods

**Hallucination Prevention:**
- Restaurant existence validation
- Schedule accuracy checks (regex-based)
- Price consistency verification
- Department/city coherence

## Deployment

Configured for Render.com with:
- Python 3.12 runtime
- Auto-rebuild embeddings on deploy
- Weekly scraping via GitHub Actions (Thursday 2am)

See `DEPLOYMENT.md` for complete guide.

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: RAG system design, data flow, performance metrics
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment guide for Render.com
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)**: AI agent development guidelines


## Author & Copyright

**Developer:** Abdoulaye SALL  
**LinkedIn:** [linkedin.com/in/abdoulaye-sall](https://www.linkedin.com/in/abdoulaye-sall/)  
**Year:** 2025

**Skills Demonstrated:**
- RAG (Retrieval-Augmented Generation) architecture
- Agentic AI systems with tool calling
- Production FastAPI deployment
- FAISS semantic search optimization
- OpenAI GPT-4 integration
- Web scraping (JSON-LD Schema.org)
- Hallucination detection & prevention

**License:** All rights reserved. Portfolio demonstration.

**Client:** Bolkiri - Vietnamese Street Food Restaurant Chain  
**Website:** [bolkiri.fr](https://bolkiri.fr)

