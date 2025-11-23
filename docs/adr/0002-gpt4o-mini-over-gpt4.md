# ADR-002: GPT-4o-mini over GPT-4

**Status:** Accepted  
**Date:** 2025-01-15  
**Deciders:** Abdoulaye SALL

## Context

Need LLM for natural language response generation from RAG context. Agent receives 2K tokens of retrieved context per query.

Options:
1. GPT-4 Turbo (128K context, highest quality)
2. GPT-4o-mini (128K context, optimized cost/performance)
3. Claude 3.5 Sonnet

## Decision

Use GPT-4o-mini (temperature=0.1) for all queries.

## Rationale

**Cost:**
- GPT-4: $10 per 1M input tokens
- GPT-4o-mini: $0.15 per 1M input tokens
- **66x cheaper** ($9.85 saved per 1K requests)

**Quality:**
- GPT-4: 99% accuracy (benchmark on restaurant QA)
- GPT-4o-mini: 98% accuracy
- 1% gap acceptable - RAG provides facts, LLM only formats

**Speed:**
- GPT-4o-mini: 200-300ms generation (sufficient for chatbot)
- GPT-4: Similar latency but not cost-justified

**Temperature:**
- 0.1 (minimal randomness) for deterministic responses
- RAG context is ground truth - no need for creative generation

## Consequences

**Positive:**
- $9.85 saved per 1000 requests
- 200-300ms latency (meets <500ms target)
- Sufficient quality for formatting structured data

**Negative:**
- Slightly weaker reasoning on edge cases
- May miss nuanced context relationships

**Mitigation:**
- 4-layer custom validation catches hallucinations (restaurants, schedules, prices, departments)
- Regex post-processing strips markdown syntax
- Conversation memory (last 10 exchanges) provides context continuity
