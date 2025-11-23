# ADR-003: 100% RAG Architecture (Zero Hardcoded Data)

**Status:** Accepted  
**Date:** 2025-01-15  
**Deciders:** Abdoulaye SALL

## Context

Restaurant data (menus, schedules, locations) changes periodically. Need strategy for keeping chatbot responses accurate.

Options:
1. Hardcode data in Python code (constants, dicts)
2. Hybrid (code + KB file)
3. 100% RAG from single JSON KB

## Decision

Single source of truth: `bolkiri_knowledge_industrial_2025.json`. Zero hardcoded menus/schedules/locations in Python code.

## Rationale

**Maintenance:**
- Menu change: Edit JSON only (no code deploy)
- Hybrid: Risk KB/code mismatch → inconsistent responses
- 100% RAG: Impossible to have drift

**Automation:**
- Weekly scraper updates KB (GitHub Actions cron)
- FAISS auto-rebuilds on deploy
- Zero manual intervention

**Consistency:**
- All 8 tools query same KB
- No "code says X but KB says Y" bugs

## Consequences

**Positive:**
- Menu changes: JSON edit only (vs full deploy)
- Zero KB/code drift bugs
- Weekly auto-updates (scraper + CI/CD)

**Negative:**
- 5-10ms RAG overhead per query
- Slightly more complex code (RAG wrapper layer)

**Mitigation:**
- 5-10ms acceptable for <500ms latency target (RAG is 2% of total time)
- `EnrichedKnowledgeBase` class abstracts RAG complexity (clean API for agent)

## Implementation

```python
# All data from KB, no hardcoded menus
kb = EnrichedKnowledgeBase()
restaurants = kb.get_all_restaurants()  # From JSON
menu = kb.get_all_menu_items()          # From JSON
```

**Update flow:**
```
Website Change → Scraper (Thursday 2am) → KB JSON updated 
→ Git push → Render deploy → FAISS rebuild → New data live
```
