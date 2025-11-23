# Architecture Decision Records (ADRs)

Quantified technical decisions for Bolkiri Agentic RAG chatbot.

## Summary Table

| ADR | Decision | Key Metric | Trade-off |
|-----|----------|------------|-----------|
| [001](0001-faiss-over-pinecone.md) | FAISS over Pinecone | $0 vs $70/month, 5-10ms vs 50-80ms | Manual scaling if 100x growth |
| [002](0002-gpt4o-mini-over-gpt4.md) | GPT-4o-mini over GPT-4 | 66x cheaper ($0.15 vs $10/1K req) | -1% accuracy edge cases |
| [003](0003-100-percent-rag.md) | 100% RAG architecture | Zero manual KB updates | 5-10ms query overhead |
| [004](0004-agentic-tools.md) | Agentic tools vs mega-prompt | 20x cheaper (2K vs 40K tokens) | More complex code |
| [005](0005-custom-validation.md) | Custom validators vs frameworks | 40x faster (5ms vs 200ms) | Manual maintenance |
| [006](0006-json-logging.md) | JSON logs vs print statements | Production observability (ELK/Datadog) | +1ms overhead per log |
| [007](0007-weekly-scraping.md) | Weekly scraping vs real-time API | No API dependency, free tier | Max 1-week stale data |
| [008](0008-json-file-over-db.md) | JSON file vs database | Git version control, <1ms load | No concurrent writes |

## Impact Metrics

**Cost:** $840/year saved (FAISS), $9.85/1K requests saved (GPT-4o-mini), 95% token reduction (agentic tools)

**Performance:** ~500ms avg latency (5ms FAISS + 10ms validation + 200-700ms LLM), 99.5% uptime (Render.com + UptimeRobot)

**Reliability:** <2% hallucination rate, 27/27 tests passing (100%), zero manual KB maintenance, auto-recovery on deploy

## Reading Guide

Format: Decision → Quantified benefits → Trade-offs + mitigation

ADRs are immutable. New decisions create new numbered files.
