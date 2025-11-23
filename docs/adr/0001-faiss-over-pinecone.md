# ADR-001: FAISS over Pinecone

**Status:** Accepted  
**Date:** 2025-01-15  
**Deciders:** Abdoulaye SALL

## Context

Need vector search for semantic RAG retrieval across 20 restaurants, 32 menu items, 19 pages (70 total embeddings, 148KB JSON).

Options:
1. Local FAISS (IndexFlatIP)
2. Cloud vector DB (Pinecone, Weaviate, Qdrant)

## Decision

Use local FAISS IndexFlatIP for exact cosine similarity search.

## Rationale

**Cost:**
- FAISS: $0 (local compute)
- Pinecone starter: $70/month = $840/year
- Break-even: Never (current scale)

**Latency:**
- FAISS: 5-10ms (in-memory, no network)
- Pinecone: 50-80ms (API call + network overhead)
- 8-16x faster for <10K vectors

**Scale:**
- Current: 70 embeddings
- Growth: +5 restaurants/year = +20 embeddings/year
- FAISS efficient until: ~10K vectors (4+ years runway)

## Consequences

**Positive:**
- Zero cost
- 8x faster queries
- No external dependency (works offline)
- Full control (custom index params)

**Negative:**
- Manual scaling if 100x growth (acceptable - not expected)
- No built-in replication (mitigated - stateless backend on Render)
- Rebuild index on each deploy (70ms rebuild time, acceptable)

**Mitigation:**
- If scale exceeds 10K vectors: Migrate to Pinecone with same IndexFlatIP config (drop-in replacement)
- Cache embeddings between deploys (REBUILD_EMBEDDINGS=false env var)
