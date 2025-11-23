# Bolkiri RAG Chatbot - Production Agentic AI with Anti-Hallucination

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-purple)
![Tests](https://img.shields.io/badge/Tests-24%2F24%20passing-brightgreen)
![License](https://img.shields.io/badge/License-Proprietary-red)

24/7 multilingual customer support chatbot with 100% RAG architecture and <2% hallucination rate.

## Problem & Solution

**Challenge:** 20-location restaurant chain requires 24/7 multilingual support for menu/location/schedule queries.

**Solution:** Agentic RAG with auto-updating knowledge base (weekly scraping) and 4-layer anti-hallucination validation.

**Impact:** <2% hallucination rate, zero manual KB maintenance, <500ms response time.

## Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **AI**: OpenAI GPT-4o-mini + Agentic tool calling (9 tools)
- **RAG**: FAISS semantic search (IndexFlatIP, 1536-dim embeddings)
- **KB**: Automated web scraping (BeautifulSoup, JSON-LD Schema.org)
- **Deployment**: Render.com (750h/month free tier)
- **CI/CD**: GitHub Actions (weekly KB updates)

## Architecture Principles

- **100% RAG**: Single source of truth (bolkiri_knowledge_industrial_2025.json), zero hardcoded data
- **Agentic Reasoning**: Multi-step tool calling (9 specialized functions)
- **Hallucination Prevention**: 4-layer validator (restaurants/schedules/prices/departments)
- **Multilingual**: Auto-detects French/Vietnamese/English
- **Auto-Update**: Weekly scraping via GitHub Actions

## Quick Start

### Live Demo

Live chatbot: https://asall94.github.io/bolkiri-chatbot/

### Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/asall94/bolkiri-chatbot.git
cd bolkiri-chatbot

# Configure environment
echo "OPENAI_API_KEY=sk-your-key" > .env

# Run with Docker Compose
docker-compose up -d

# Access at http://localhost:8000
```

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure OpenAI
echo "OPENAI_API_KEY=sk-your-key" > .env
echo "REBUILD_EMBEDDINGS=false" >> .env  # true on first run

# Launch backend
python main.py  # http://localhost:8000

# Run tests
python -m pytest tests/ --cov=ai_agent --cov-report=html

# Test endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Quels restaurants en Essonne?"}'
```

## Architecture Details

**System Architecture:**
```mermaid
graph TB
    subgraph "Client Layer"
        A[User Query] --> B[FastAPI /chat endpoint]
    end
    
    subgraph "Agent Layer"
        B --> C[AI Agent<br/>ai_agent.py]
        C --> D{Tool Selection<br/>GPT-4o-mini}
        D --> E1[search_knowledge]
        D --> E2[get_restaurants]
        D --> E3[filter_menu]
        D --> E4[get_hours]
        D --> E5[get_contact]
        D --> E6[recommend_dish]
        D --> E7[get_restaurant_info]
        D --> E8[get_menu]
        D --> E9[find_nearest]
    end
    
    subgraph "RAG Layer"
        E1 --> F[RAG Engine<br/>rag_engine.py]
        E2 --> G[Enriched KB<br/>knowledge_base_enriched.py]
        E3 --> G
        E4 --> G
        E5 --> G
        E6 --> G
        E7 --> G
        E8 --> G
        F --> H[(FAISS Index<br/>IndexFlatIP)]
        G --> I[(Knowledge Base<br/>bolkiri_knowledge_industrial_2025.json)]
    end
    
    subgraph "Validation Layer"
        C --> J{Anti-Hallucination<br/>4 Validators}
        J --> J1[Restaurant Existence]
        J --> J2[Schedule Format]
        J --> J3[Price Consistency]
        J --> J4[Department Coherence]
    end
    
    subgraph "LLM Layer"
        D -.token usage.-> K[OpenAI API<br/>GPT-4o-mini]
        F -.embeddings.-> L[OpenAI API<br/>text-embedding-ada-002]
    end
    
    J --> M[Final Response]
    M --> B
    
    subgraph "Auto-Update Pipeline"
        N[GitHub Actions<br/>Weekly Cron] --> O[Scraper<br/>scraper_industrial_2025.py]
        O --> P[Bolkiri Website<br/>JSON-LD + HTML]
        O --> I
        I --> Q[Rebuild FAISS<br/>on Deploy]
        Q --> H
    end
    
    style C fill:#e1f5ff
    style F fill:#ffe1e1
    style G fill:#ffe1e1
    style J fill:#fff4e1
    style K fill:#e8f5e9
    style L fill:#e8f5e9
```

## Agentic Architecture

**Tool-First Design:** Agent never answers from memory. Every response requires tool execution to retrieve RAG context.

**Execution Flow:**
```
User Query → Intent Analysis → Tool Selection (GPT-4o-mini) 
→ Parallel Tool Execution (1-3 tools) → Context Retrieval (FAISS) 
→ Response Synthesis (temp=0.1) → 4-Layer Validation → Final Answer
```

**Multi-Step Reasoning Examples:**

1. **Query:** "Do you have vegetarian options in Essonne?"
   ```
   Step 1: detect_department("Essonne") → Extract "91"
   Step 2: filter_menu(vegetarian=True) → 12 veggie dishes
   Step 3: get_restaurant_info("91") → Corbeil-Essonnes location
   Step 4: Synthesize → "Yes, Bolkiri Corbeil-Essonnes (91) offers 12 vegetarian dishes including..."
   ```

2. **Query:** "What's your menu and where are you located?"
   ```
   Step 1: get_menu() → Full 32-dish menu with prices
   Step 2: get_restaurants() → All 20 locations
   Step 3: Synthesize → Combined response with menu + addresses
   ```

3. **Query:** "Spring rolls available?"
   ```
   Step 1: search_knowledge("spring rolls") → RAG retrieval (FAISS cosine similarity)
   Step 2: Extract dish data from context (name, price, description)
   Step 3: Synthesize → "Yes, Nems (spring rolls) available at 6.50€..."
   ```

**9 Available Tools:**
- `search_knowledge`: FAISS semantic search
- `get_restaurants`: List 20 locations
- `get_restaurant_info`: Query by city/department (91/94/77/78)
- `get_menu`: Full menu with prices
- `filter_menu`: Filter by criteria (vegetarian/vegan/price)
- `get_contact`: Phone/email/social media
- `find_nearest_restaurant`: GPS-based proximity search
- `detect_department`: Extract department from natural language
- `recommend_dish`: Personalized suggestions

**Key Components:**
- `ai_agent.py`: Tool calling, planning, validation
- `rag_engine.py`: FAISS semantic search
- `scraper_industrial_2025.py`: JSON-LD + HTML parser
- `knowledge_base_enriched.py`: RAG wrapper with domain methods

**Anti-Hallucination Validation (4 layers):**
1. **Restaurant existence**: Whitelist of 20 KB names
2. **Schedule format**: Regex validation
3. **Price consistency**: Strips hallucinated prices
4. **Department coherence**: Maps 91/94/77/78 to cities

## Deployment

Render.com deployment:
- Python 3.12 runtime
- Auto-rebuild embeddings
- Weekly scraping (Thursday 2am UTC)

See `DEPLOYMENT.md` for full guide.

## Documentation

- **[Architecture Decision Records](docs/adr/README.md)**: 8 technical decisions with quantified trade-offs
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Production deployment guide
- **[RAG_ARCHITECTURE.html](docs/RAG_ARCHITECTURE.html)**: Interactive architecture visualization

## Testing & Quality

- **Tests**: 24/24 passing (100%)
- **Coverage**: 42% on ai_agent.py
- **Framework**: pytest + pytest-cov + pytest-mock
- **Mocks**: EnrichedKnowledgeBase, OpenAI API
- **CI/CD**: GitHub Actions weekly scraping

```bash
# Run tests
python -m pytest tests/ -v

# With coverage report
python -m pytest tests/ --cov=ai_agent --cov-report=html
```

## Author & Copyright

**Abdoulaye SALL** - Lead AI Engineer  
[LinkedIn](https://linkedin.com/in/abdoulaye-sall/)

**Skills Demonstrated:**
- Agentic RAG architecture with multi-step tool calling (9 specialized functions)
- Anti-hallucination system with 4-layer validation (<2% error rate)
- GPS-based geolocation with Haversine distance calculation (Nominatim API)
- FAISS vector search optimization (5-10ms latency, $840/year saved vs Pinecone)
- Production FastAPI deployment on Render.com with auto-scaling
- OpenAI GPT-4o-mini integration with function calling (66x cheaper than GPT-4)
- Automated knowledge base updates via GitHub Actions CI/CD
- Web scraping with JSON-LD + BeautifulSoup for structured data extraction
- Docker containerization with multi-stage builds
- pytest unit testing with 100% pass rate (24/24 tests)
- Structured JSON logging for production observability

**License:** Proprietary - See LICENSE for details

**Business Context:** 24/7 customer support automation for Bolkiri Vietnamese restaurant chain (Bolkiri.fr - 20 locations)