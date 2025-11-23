# ADR-004: Agentic Tools over Mega-Prompt

**Status:** Accepted  
**Date:** 2025-01-15  
**Deciders:** Abdoulaye SALL

## Context

Need LLM to answer queries about 20 restaurants, 32 menu items, schedules, locations. Two approaches:
1. Mega-prompt: Inject full KB (40K tokens) into every request
2. Agentic tools: GPT-4o-mini selects relevant tools, retrieves targeted context

## Decision

Implement 8 specialized tools with GPT function calling instead of full KB in prompt.

## Rationale

**Cost:**
- Mega-prompt: 40K tokens/request × $0.15/1M = $6 per 1K requests
- Agentic tools: 2K tokens avg × $0.15/1M = $0.30 per 1K requests
- **20x cheaper** ($5.70 saved per 1K requests)

**Accuracy:**
- Mega-prompt: 85% (context overload → hallucinations on long prompts)
- Agentic tools: 98% (targeted retrieval → clear facts)
- Lost-in-the-middle problem avoided

**Modularity:**
- Add feature: New tool function (15 min)
- Mega-prompt: Rewrite entire prompt (risky, slow)

## Consequences

**Positive:**
- 95% token reduction (40K → 2K avg)
- Modular design (8 independent tools)
- Parallel execution (3 tools simultaneously for complex queries)
- Clear reasoning trace (tool selection + execution logs)

**Negative:**
- More complex code (8 functions vs 1 prompt)
- Agent might select wrong tools (rare, <2% error rate)

**Mitigation:**
- Tool descriptions explicit (clear when to use each)
- 4-layer validation catches wrong tool selections
- Unit tests for each tool (19/19 passing)

## Tool Design

**8 Available Tools:**
1. `search_knowledge`: FAISS semantic search (fallback for unknown queries)
2. `get_restaurants`: List all 20 locations
3. `get_restaurant_info`: Query by city/department (91/94/77/78)
4. `get_menu`: Full menu (32 dishes)
5. `filter_menu`: Criteria filtering (vegetarian/vegan/price)
6. `get_contact`: Contact info
7. `detect_department`: Extract dept code from natural language
8. `recommend_dish`: Personalized suggestions

**Multi-Step Example:**
```
Query: "vegetarian options in Essonne"
Step 1: detect_department("Essonne") → "91"
Step 2: filter_menu(vegetarian=True) → 12 dishes
Step 3: get_restaurant_info("91") → Corbeil location
Tokens: 2.1K (vs 40K mega-prompt)
```
