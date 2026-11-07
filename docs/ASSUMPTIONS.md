# Assumptions

All open decisions resolved during planning (Nov 7, 2026). Record any further changes here with date and reason.

---

## Resolved Decisions

| # | Decision | Resolution | Notes |
|---|---|---|---|
| 1 | AI phone screen technology | Mock adapter in Phase 1; Plivo in Phase 2 | Interface designed now so swap is one env var |
| 2 | AI technical interview technology | Mock adapter in Phase 1; Plivo / TBD in Phase 2 | Same pattern as phone screen |
| 3 | LLM provider | Mock adapter in Phase 1 (structured dummy JSON responses); real LLM API in Phase 2 | All prompts versioned in /prompts now; adapter wired later |
| 4 | Candidate sourcing — Phase 1 | GitHub public API (no key) + Stack Overflow public API (no key) + DuckDuckGo search (duckduckgo-search library, no key) + Mock adapter | No scraping of sites that prohibit it |
| 5 | Candidate sourcing — Phase 2 | Juicebox API (dev team to supply key) | Adapter interface built in Phase 1 |
| 6 | WhatsApp outreach | Mock adapter in Phase 1; Gupshup in Phase 2 | Official WhatsApp Business Platform via Gupshup BSP |
| 7 | Contact enrichment | Mock adapter in Phase 1; Apollo.io / Juicebox in Phase 2 | Waterfall: cache → published → primary → fallback |
| 8 | Embeddings | Mock (zero/random vectors) in Phase 1; real embedding model (sentence-transformers or API) in Phase 2 | pgvector column present from Phase 1 |
| 9 | Universal platform database | Platform-owned shared candidate pool; all workspaces can read it, none see each other's data; write only via platform admin role | Separate schema/table from client data |
| 10 | Client database | Fully isolated per workspace via row-level security (workspace_id) | Clients cannot access each other's candidates, labels, or rules |
| 11 | Phase 1 live sending | Mock-only outreach; no real messages sent | All outreach adapters are mocks |
| 12 | Escalation wait | 48 hours before next channel; configurable per workspace | Default stored in workspace settings |
| 13 | Interview question approval | Recruiter approves question set before any call runs | Stored as confirmed rules in DB |
| 14 | WhatsApp provider (long term) | Gupshup (Business Solution Provider) | Not Meta Cloud API directly |
| 15 | Hosting / data residency | To be confirmed before Phase 2; India-hosted storage likely required for DPDP Act compliance | No production data processed until confirmed |
| 16 | DPO / compliance owner | Required before any live candidate data is processed (Phase 2 gate) | DPDP Act, GDPR, CCPA obligations |
| 17 | ROI assumptions | 14 recruiter-hours per hire, 4 tech screen hours per hire, 250 hires/year, 50% recruiter reduction, 75% tech screen reduction — placeholders to validate in pilot | Platform cost placeholder: ₹3 lakh/year |
| 18 | Telephony provider | Plivo (Phase 2) | Mock in Phase 1 |

---

## Stack Assumptions

| Component | Choice | License | Reason |
|---|---|---|---|
| Backend | Python 3.12 + FastAPI + SQLAlchemy + Alembic | MIT / BSD | Async support, structured output easy |
| Database | PostgreSQL 16 + pgvector | PostgreSQL License / Apache 2.0 | Vector similarity for preference model |
| Background jobs | Redis + Celery | MIT / BSD | Mature, retryable, rate-limit friendly |
| Frontend | Next.js 14 + TypeScript + Tailwind CSS | MIT | App Router, SSE support |
| UI primitives | Radix Primitives | MIT | Accessible, unstyled |
| Data tables | TanStack Table v8 | MIT | Virtualization for large candidate pools |
| Charts / KPIs | Tremor | Apache 2.0 | Built on Tailwind + Recharts |
| Command palette | cmdk | MIT | Keyboard-first navigation |
| Icons | Lucide | MIT | Consistent, quiet |
| Animations | Motion (Framer Motion) | MIT | Restrained transitions, respects reduced-motion |
| Infrastructure | Docker Compose | Apache 2.0 | Local-first Phase 1 |
| Backend tests | pytest | MIT | Standard |
| E2E tests | Playwright | Apache 2.0 | Calibration deck, rule builder, outreach timeline |

All licenses confirmed as permissive (MIT / Apache 2.0 / PostgreSQL License). No copyleft dependencies.

---

## LinkedIn

LinkedIn scraping is explicitly prohibited by their Terms of Service. The build prompt itself requires respecting each site's ToS. LinkedIn is therefore excluded from Phase 1 sourcing. Access via LinkedIn Talent Solutions API (enterprise, paid) can be considered in a later phase after legal review.
