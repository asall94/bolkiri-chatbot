# ADR-006: Structured JSON Logging over Print Statements

**Status:** Accepted  
**Date:** 2025-01-23  
**Deciders:** Abdoulaye SALL

## Context

Need production observability for debugging, monitoring, and incident response. Original implementation used text-based print statements (`[OK]`, `[WARN]`, `[ERROR]`).

Options:
1. Keep print statements (simple, human-readable console)
2. Python logging module (stdlib, structured levels)
3. Structured JSON logs (timestamp, level, context fields)

## Decision

Implement structured JSON logging with custom formatter (timestamp, level, logger, message, extra context).

## Rationale

**Production Observability:**
- JSON logs → ELK/Datadog/Splunk ingestion (no parsing needed)
- Print statements → require regex parsing (brittle, slow)
- Structured queries: `level:ERROR AND validation_result:invalid_corrected`

**Context Preservation:**
- JSON: `{"level": "WARNING", "phrase": "pas de restaurant", "validation_result": "hallucination"}`
- Print: `[WARN] HALLUCINATION: 'pas de restaurant' despite positive context` (unstructured)

**Standards:**
- Industry standard for microservices (12-factor app methodology)
- Compatible with cloud log aggregation (AWS CloudWatch, GCP Logging)

## Consequences

**Positive:**
- Log aggregation ready (ELK stack, Datadog)
- Structured queries (filter by level, error_type, validation_result)
- ISO 8601 timestamps (timezone-aware)
- Extra context fields (restaurant_count, tool_name, user_query)

**Negative:**
- +1ms overhead per log call (JSON serialization)
- Less human-readable in raw console (mitigated - use jq for local dev)

**Mitigation:**
- 1ms overhead negligible (<0.2% of 500ms target latency)
- Local dev: `python main.py | jq` for pretty output
- Production: Logs ingested by Render.com → structured by default

## Implementation

```python
# logger_config.py
class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            # Extra fields from record
            **getattr(record, 'extra', {})
        })

# Usage
logger.warning("Price hallucination detected", 
               extra={"response_prices": prices, "context_empty": True})
```

**Log Examples:**
```json
{"timestamp": "2025-01-23T09:02:35.587249Z", "level": "INFO", "logger": "__main__", "message": "Agent initialized successfully", "restaurant_count": 20}

{"timestamp": "2025-01-23T09:05:12.123456Z", "level": "WARNING", "logger": "ai_agent", "message": "Restaurant hallucination detected", "phrase": "n'avons pas de restaurant", "validation_result": "negative_phrase_despite_positive_context"}
```
