# Bolkiri Chatbot - Agentic AI Assistant

Production-ready **agentic AI system** for Bolkiri Vietnamese restaurant chain. Built with RAG architecture, tool calling, and multi-step reasoning.

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **AI**: OpenAI GPT-4o-mini + **Agentic tool calling** (8 tools)
- **RAG**: FAISS semantic search + custom retrieval pipeline
- **KB**: Automated web scraping (BeautifulSoup, JSON-LD Schema.org)
- **Deployment**: Render.com with auto-scaling
- **CI/CD**: Automated pipeline (weekly KB updates)

## Key Features

- **Agentic AI**: Multi-step reasoning, tool calling, context planning
- **100% RAG Architecture**: Zero hardcoded data, single source of truth
- **Hallucination Prevention**: 4-type validator (restaurants/schedules/prices/departments)
- **Multilingual**: Auto-detects and responds in query language
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

**Agentic Pipeline:**
```
User Query → Tool Planning → Multi-tool Execution → Context Aggregation → LLM → Validation → Response
```

**8 Available Tools:**
- `search_knowledge`: RAG semantic search
- `get_restaurants`: List all 20 locations
- `get_restaurant_info`: Query by city/department
- `get_menu`: Full menu retrieval
- `filter_menu`: Criteria-based filtering
- `get_contact`: Contact information
- `get_hours`: Opening schedules
- `recommend_dish`: Personalized suggestions

**Key Components:**
- `ai_agent.py`: **Agentic core** (tool calling, planning, validation)
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
- Weekly scraping via automated CI/CD (Every Thursday at 2am)

See `DEPLOYMENT.md` for complete guide.

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: RAG system design, data flow, performance metrics
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment guide for Render.com
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)**: AI agent development guidelines

## Language Notes

**Code & Docs:** 
- English (industry standard, portfolio-ready)
- Chatbot responds in user's language (French/Vietnamese/English/Others auto-detected)

**French Elements** (business context - bolkiri.fr):
- Knowledge base content in `bolkiri_knowledge_industrial_2025.json` (scraped from French website)


## Author & Copyright

**AI Engineer:** Abdoulaye SALL  
**LinkedIn:** [linkedin.com/in/abdoulaye-sall](https://www.linkedin.com/in/abdoulaye-sall/)  
**Year:** 2025

**Skills Demonstrated:**
- RAG (Retrieval-Augmented Generation) architecture
- Agentic AI systems with tool calling
- Production FastAPI deployment
- FAISS semantic search optimization
- OpenAI GPT-4 integration
- Automated CI/CD pipelines 
- Web scraping (JSON-LD Schema.org)
- Hallucination detection & prevention

**License:** Proprietary - See [LICENSE](LICENSE) for details.

**Business Context:** Bolkiri - Vietnamese Street Food Restaurant Chain  
**Website:** [bolkiri.fr](https://bolkiri.fr)