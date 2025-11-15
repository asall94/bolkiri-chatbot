# RAG Architecture Overview

Technical documentation for Bolkiri Chatbot's Retrieval-Augmented Generation system.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          User Query                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Semantic Search (FAISS)                       │
│  - Query embedding via OpenAI text-embedding-ada-002            │
│  - Vector similarity search (cosine distance)                    │
│  - Top-5 context retrieval                                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Context Aggregation                            │
│  - Merge retrieved documents                                     │
│  - Add restaurant metadata                                       │
│  - Inject department mappings (91→Corbeil, etc.)                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                LLM Generation (GPT-4o-mini)                      │
│  - System prompt: French language expert                         │
│  - Context injection (retrieved docs)                            │
│  - Temperature: 0.1 (deterministic)                              │
│  - Max tokens: 500                                               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Response Validation                             │
│  1. Restaurant existence check                                   │
│  2. Schedule accuracy (regex-based)                              │
│  3. Price consistency                                            │
│  4. Department/city coherence                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Validated Response                            │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Knowledge Base (`bolkiri_knowledge_industrial_2025.json`)

**Structure:**
```json
{
  "version": "4.0_industrial",
  "total_restaurants": 20,
  "restaurants": [...],
  "pages_par_categorie": {
    "menu": [31 items],
    "fidelite": [1 page],
    "service_client": [1 page],
    "concept": [2 pages],
    "autres": [14 pages]
  }
}
```

**Generation:** `scraper_industrial_2025.py`
- Scrapes 19 pages + 20 restaurant pages
- Parses JSON-LD Schema.org for structured data
- Chunks menu into individual dishes
- Injects clickable links (HTML format)

### 2. RAG Engine (`rag_engine.py`)

**Technology:** FAISS (Facebook AI Similarity Search)

**Embedding Model:** OpenAI `text-embedding-ada-002`
- Dimension: 1536
- Cost: $0.0001 per 1K tokens

**Index Type:** `IndexFlatIP` (Inner Product)
- Exact search (no approximation)
- Optimized for small datasets (<10K docs)

**Search Flow:**
```python
query → embed(query) → FAISS.search(top_k=5) → ranked_results
```

### 3. AI Agent (`ai_agent.py`)

**Agentic Features:**
- Tool calling (8 tools available)
- Multi-step reasoning
- Context planning
- Response validation

**Tools:**
1. `search_knowledge`: General RAG search
2. `get_restaurants`: List all restaurants
3. `get_restaurant_info`: Query by city/department
4. `get_menu`: Full menu retrieval
5. `filter_menu`: Criteria-based filtering
6. `get_contact`: Contact info
7. `get_hours`: Opening hours
8. `recommend_dish`: Personalized recommendations

### 4. Response Validator

**Hallucination Detection:**

1. **Restaurant Contradictions**
   - Detects: "no restaurant in 91" when context says Corbeil exists
   - Fix: Returns corrected response with actual data

2. **Schedule Inaccuracies**
   - Regex: `\d{1,2}:\d{2}-\d{1,2}:\d{2}`
   - Validates: No time rounding (11:30 NOT 11h30)

3. **Price Inconsistencies**
   - Detects: Response price > 2x context max
   - Fix: Replaces aberrant prices

4. **Department/City Coherence**
   - Mapping: 91→Corbeil, 94→Ivry, 78→Mureaux, 77→Lagny
   - Validates: Department mention matches city in context

## Data Flow

### KB Update Cycle

```
Weekly (Thursday 2am)
      │
      ▼
GitHub Actions: Run scraper
      │
      ▼
Generate new JSON (20 restaurants, 19 pages)
      │
      ▼
Commit to repo
      │
      ▼
Render auto-deploy
      │
      ▼
Rebuild FAISS embeddings (if REBUILD_EMBEDDINGS=true)
      │
      ▼
Production update complete
```

### Request Flow

```
User: "Do you have nems?"
      │
      ▼
Semantic search: query="nems"
      │
      ▼
FAISS returns:
  1. ASSORTIMENT FRITURE (score: 0.85)
  2. FORMULE BÒ BÚN (score: 0.78)
  3. ...
      │
      ▼
Context injected into GPT-4o-mini
      │
      ▼
LLM generates response mentioning both dishes
      │
      ▼
Validator checks: nems mentioned? ✓ Links present? ✓
      │
      ▼
Return validated response with clickable menu link
```

## Performance Metrics

**Embedding Generation:**
- Time: ~0.5s per batch (10 docs)
- Cache: Stored in `embeddings_cache.pkl`

**Search Latency:**
- FAISS query: <10ms
- Total RAG: ~200-500ms (including LLM)

**Accuracy:**
- Hallucination prevention: ~95% (4 validators)
- Context relevance: Top-5 retrieval ensures high precision

## Key Design Decisions

### Why FAISS over ChromaDB?

**FAISS advantages:**
- Faster for small datasets (<10K docs)
- No external service required
- Lightweight (fits in memory)
- Local caching

**ChromaDB drawbacks:**
- Overkill for 50 documents
- Requires persistent storage
- More complex deployment

### Why Single JSON KB?

**Benefits:**
- Single source of truth
- Easy version control (git)
- Fast loading (<100ms)
- Simple backup/restore

**Tradeoffs:**
- Not suitable for >100K docs
- Requires full reload on update

### Why Weekly Scraping?

**Rationale:**
- Restaurant data changes infrequently
- Reduces API costs
- Avoids rate limiting
- Thursday 2am = low traffic time

## Troubleshooting

### Low Search Quality

**Symptoms:** Irrelevant results, missing context

**Solutions:**
1. Increase `limit` in `search()` (default: 5)
2. Check query embedding quality
3. Verify KB content completeness
4. Rebuild embeddings cache

### Validation False Positives

**Symptoms:** Valid responses marked invalid

**Solutions:**
1. Review regex patterns in `_validate_response()`
2. Adjust threshold (e.g., price multiplier 2x → 3x)
3. Check department mappings

### Slow Response Times

**Symptoms:** >2s latency

**Solutions:**
1. Cache embeddings (done by default)
2. Reduce `max_tokens` in LLM call
3. Optimize FAISS index (use `IndexIVFFlat` for >10K docs)

## Future Improvements

1. **Hybrid Search:** Combine vector + keyword (BM25)
2. **Reranking:** Add cross-encoder for better top-k
3. **Streaming:** Implement SSE for incremental responses
4. **A/B Testing:** Track validation accuracy metrics
5. **Multilingual Embeddings:** Use `multilingual-e5` for better Vietnamese support
