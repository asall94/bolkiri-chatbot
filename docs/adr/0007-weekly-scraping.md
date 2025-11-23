# ADR-007: Weekly Scraping over Real-Time API

**Status:** Accepted  
**Date:** 2025-01-15  
**Deciders:** Abdoulaye SALL

## Context

Need to keep KB synchronized with Bolkiri website (bolkiri.fr). Restaurant data changes infrequently (new locations quarterly, menu updates monthly).

Options:
1. Real-time: Scrape on every query (always fresh)
2. Webhook: Bolkiri API notifies on changes
3. Scheduled: Weekly scraping via cron job

## Decision

GitHub Actions weekly cron (Thursday 2am UTC) scraping + automatic KB update.

## Rationale

**No API Dependency:**
- Bolkiri has no public API
- Building webhook integration = development time + maintenance burden
- Website scraping = zero external dependencies

**Cost:**
- GitHub Actions: 2000 min/month free tier
- Weekly scrape: ~2 min/week = 8 min/month (well within free tier)
- Real-time scraping: API costs + rate limiting issues

**Freshness:**
- Max staleness: 1 week
- Acceptable: Restaurant info changes monthly (menus), quarterly (locations)
- Users tolerate week-old data for this domain

**Reliability:**
- Works even if bolkiri.fr temporarily down (cached KB)
- No runtime dependency on external site uptime

## Consequences

**Positive:**
- Zero API costs
- No external API dependency
- Free GitHub Actions tier sufficient
- Atomic KB updates (full replace, no partial corruption)

**Negative:**
- Max 1-week stale data
- Scraper maintenance if site HTML changes

**Mitigation:**
- Weekly schedule adequate (data rarely changes daily)
- JSON-LD structured data (Schema.org) reduces HTML fragility
- Scraper has fallback HTML parsing if JSON-LD missing
- Manual trigger available (`/refresh` endpoint for urgent updates)

## Implementation

**Scraping Strategy:**
1. Primary: JSON-LD Schema.org (structured, stable)
2. Fallback: BeautifulSoup HTML parsing (if JSON-LD missing)

**Update Flow:**
```yaml
# .github/workflows/auto-scraping.yml
on:
  schedule:
    - cron: '0 2 * * 4'  # Thursday 2am UTC

jobs:
  scrape:
    - python scraper_industrial_2025.py
    - git commit bolkiri_knowledge_industrial_2025.json
    - git push
    - Render auto-deploy → FAISS rebuild → new data live
```

**Manual Override:**
```bash
# Emergency update (if menu changes same day)
curl -X POST https://bolkiri-chatbot.onrender.com/refresh
```
