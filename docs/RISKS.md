# Risks

---

## Legal / Regulatory

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| DPDP Act non-compliance (India) | High if unmitigated | Critical | Appoint DPO before Phase 2; privacy-by-default settings; audit log from Phase 1; lawful basis recorded per profile |
| GDPR exposure for EU candidate data | Medium | High | Same controls as DPDP; data residency decision required before Phase 2; consent/opt-out from first contact |
| CCPA exposure for US candidate data | Medium | Medium | Opt-out honoured immediately; deletion requests propagated; no sale of personal data |
| WhatsApp Business Policy violation | Low (using Gupshup BSP) | High | Use only pre-approved message templates; include opt-out in every message; never bypass template approval |
| Scraping ToS violation | Low (architecture avoids it) | High | Only official APIs and licensed data providers used; LinkedIn explicitly excluded; robots.txt respected |
| AI-in-hiring bias discrimination claims | Medium | Critical | Protected attributes never used in scoring or preference model; protected-attribute test in test suite from Phase 1; human recruiter makes every final decision |

---

## Data Quality

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Entity resolution false merges (two people treated as one) | Medium | High | Confidence score threshold configurable; recruiter can split merged profiles; evidence panel shows all sources |
| Stale public profiles (GitHub/SO not updated) | High | Medium | Recency score component penalises inactive profiles; show last-active date in evidence panel |
| Low candidate pool for niche roles | Medium | Medium | Cold-start detection: if pool < 20 or all No, prompt recruiter to broaden JD |
| Scoring quality dependent on LLM mock quality | High in Phase 1 | Low (Phase 1 is demo) | Mock returns plausible structured data; replace with real LLM in Phase 2 |
| DuckDuckGo rate limiting in bulk sourcing | Medium | Low | Rate-limit handling in adapter; exponential backoff; Celery retry |

---

## Technical

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| pgvector performance at scale | Low in Phase 1 | Medium | IVFFlat index from Phase 1; HNSW available as upgrade in Phase 2 |
| Celery task duplication on restart | Medium | Medium | Idempotency keys on all tasks; deduplication check before inserting candidates |
| Redis single-point-of-failure | Low in Phase 1 (local) | Medium | Redis Sentinel / Cluster in Phase 2 |
| Docker Compose not suitable for production | High | High | Phase 1 is local-only by design; production infra decision deferred to Phase 3 |
| Embedding mock (zeros/random) breaks cosine similarity | High in Phase 1 | Low (Phase 1 is demo) | Noted in UI; mock ranker uses score components instead of embeddings |

---

## Anti-Scraping

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GitHub API rate limit (60 req/hour unauthenticated) | High for large sourcing runs | Medium | Use unauthenticated limit for Phase 1 demo; authenticated token (5000/hour) available via settings for Phase 2 |
| Stack Overflow API quota | Medium | Low | 300 requests/day without key; sufficient for Phase 1 demo scale |
| DuckDuckGo blocking | Medium | Low | duckduckgo-search library handles this; fallback to Mock adapter |

---

## Model Bias

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Preference model learns recruiter bias | Medium | Critical | Protected attributes explicitly excluded from feature set; proxy attributes (name, photo) also excluded; protected-attribute test in CI from Phase 1 |
| Cold-start overfitting to small label set | Medium | Medium | Cold-start guard: suggest calibration complete only when yes-rate stabilises and minimum label count reached |
| Calibration batch not diverse enough | Medium | Medium | Active learning selects from boundary + likely Yes + exploration share to maximise diversity |

---

## Cost

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Contact enrichment credit overrun | Low in Phase 1 (mock) | High in Phase 2 | Enrich only shortlisted/above-threshold profiles; show estimated cost before bulk run; per-workspace credit budgets with alerts |
| LLM API cost at scale | Low in Phase 1 (mock) | Medium | Prompt versioning allows model tier selection per use case; cheapest tier for scoring, capable tier for interviews |
