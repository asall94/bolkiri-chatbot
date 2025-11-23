# ADR-008: JSON File over Database

**Status:** Accepted  
**Date:** 2025-01-15  
**Deciders:** Abdoulaye SALL

## Context

Need persistent storage for KB: 20 restaurants, 32 menu items, 19 pages (148KB JSON). Data changes weekly via scraper.

Options:
1. JSON file (bolkiri_knowledge_industrial_2025.json)
2. SQLite (embedded, SQL queries)
3. PostgreSQL (production-grade, ACID)
4. MongoDB (document store, flexible schema)

## Decision

Use single JSON file as KB storage. Load into memory on startup.

## Rationale

**Simplicity:**
- No DB setup/migrations/connection pooling
- Single file = atomic updates (file replace)
- Zero configuration (no DATABASE_URL, credentials)

**Version Control:**
- JSON in git → full history (`git diff` shows exact changes)
- Database → opaque binary, no diff visibility
- Rollback = `git revert` (instant)

**Performance:**
- Load time: <1ms (148KB file → memory)
- Query time: O(1) dict lookup (restaurants by name)
- No network latency (local file)

**Scale:**
- Current: 148KB
- Growth: +5 restaurants/year = +4KB/year
- File efficient until: ~10MB (20+ years runway)

**Deployment:**
- Render.com: JSON file in repo → automatic deploy
- Database: Separate service, connection management, backups

## Consequences

**Positive:**
- Zero DB setup/maintenance
- Git version control (full audit trail)
- <1ms load time (in-memory after startup)
- Atomic updates (file replace = all-or-nothing)
- Easy local development (no DB install)

**Negative:**
- No concurrent write safety (not needed - single scraper process)
- No complex queries (not needed - simple key lookup)
- All data in memory (148KB negligible vs 512MB container)

**Mitigation:**
- Concurrent writes not a concern (single weekly scraper, no user writes)
- Complex queries not needed (agentic tools handle logic)
- Memory footprint trivial (148KB vs 512MB available)

## Implementation

```python
# knowledge_base_enriched.py
class EnrichedKnowledgeBase:
    def __init__(self):
        with open('bolkiri_knowledge_industrial_2025.json') as f:
            self.data = json.load(f)  # <1ms load
        self._restaurants = {r['nom']: r for r in self.data['restaurants']}
        self._menu = {m['nom']: m for m in self.data['menu']}
    
    def get_restaurant(self, name: str) -> dict:
        return self._restaurants.get(name)  # O(1) dict lookup
```

**Update Flow:**
```
Scraper → Write JSON → Git commit → Push → Render deploy → 
App restart → Load new JSON → FAISS rebuild → Live
```

**When to Migrate to DB:**
- KB exceeds 10MB (20+ years at current growth)
- Need concurrent writes (e.g., user-generated content)
- Complex relational queries (e.g., JOIN operations)
