# ADR-005: Custom Validation over Guardrails Frameworks

**Status:** Accepted  
**Date:** 2025-01-15  
**Deciders:** Abdoulaye SALL

## Context

Need to prevent LLM hallucinations (wrong restaurants, fake prices, incorrect schedules). Two approaches:
1. Guardrails framework (NeMo Guardrails, Guardrails AI)
2. Custom domain-specific validators

## Decision

Implement custom 4-layer validators (restaurants/schedules/prices/departments) instead of generic framework.

## Rationale

**Specificity:**
- Framework: Generic toxicity/bias checks (not relevant for restaurant chatbot)
- Custom: Domain rules (20 allowed restaurant names, schedule regex, price consistency)

**Speed:**
- Framework: 200ms (additional LLM call per validation)
- Custom: 5ms (regex + set lookup)
- **40x faster**

**Control:**
- Framework: Complex customization (DSL, YAML config)
- Custom: Add validator in 15min (Python function + unit test)

## Consequences

**Positive:**
- 5ms overhead (vs 200ms framework)
- Domain-specific rules (exact 20 restaurant names, not fuzzy match)
- Easy to extend (new validator = new function)

**Negative:**
- Manual maintenance (no framework updates)
- No pre-built toxicity detection (not needed for restaurant domain)

**Mitigation:**
- Unit tests for each validator (catch regressions)
- Validators are pure functions (easy to test)
- 19/19 tests passing (100% success rate)

## Implementation

**4-Layer Validation:**

1. **Restaurant Existence**
   ```python
   allowed_names = set(kb.get_all_restaurants())
   if restaurant not in allowed_names:
       return corrected_response
   ```

2. **Schedule Format**
   ```python
   context_hours = re.findall(r'\d{1,2}:\d{2}-\d{1,2}:\d{2}', context)
   if response_hours != context_hours:
       return "Contact restaurant directly for schedules"
   ```

3. **Price Consistency**
   ```python
   if response_has_prices and not context_has_prices:
       return strip_prices(response)
   ```

4. **Department Coherence**
   ```python
   dept_map = {"91": "Corbeil", "94": "Ivry", ...}
   if dept in query and wrong_city in response:
       return get_restaurant_info(dept)
   ```

**Metrics:**
- Hallucination rate: <2% (vs 15% baseline GPT-4o-mini without validation)
- False positives: <1% (overly aggressive corrections rare)
- Latency: 5ms avg per validation
