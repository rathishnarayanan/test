# Roadmap

---

## Phase 1 — MVP (Local, Mock-first, No API Keys)

**Goal**: Prove three things end to end with mock adapters:
1. JD → confirmed search spec → rubric → ranked, deduplicated candidate pool with evidence
2. Calibration labels visibly change the next batch and the ranking
3. Rules, outreach, phone screening, and AI technical interview run against mocks and write results to the dashboard

**Estimate**: 6–8 weeks for one full-stack developer

---

### Step 1 — Scaffold (~3–4 days)

- [ ] Project directory structure (api/, web/, docs/, prompts/, scripts/)
- [ ] Docker Compose: db (postgres+pgvector), redis, api, worker, scheduler, web
- [ ] FastAPI app skeleton, health endpoint
- [ ] SQLAlchemy models + Alembic migrations (all tables from DATA_MODEL.md)
- [ ] Adapter registry: `AdapterRegistry` class, env-var-based selection
- [ ] All Mock adapters: `MockSourceAdapter`, `MockContactAdapter`, `MockLLMAdapter`, `MockOutreachAdapter`, `MockTelephonyAdapter`, `MockInterviewAdapter`, `MockEmbeddingAdapter`
- [ ] Seed script: 3 sample JDs, 50 mock candidates, platform pool of 100, mock recruiter labeller
- [ ] `.env.example` with all variables documented
- [ ] Next.js app skeleton, Tailwind config, theme tokens, Radix + Lucide installed

**Acceptance**: `docker compose up` starts all services; health check passes; seed data loads.

---

### Step 2 — JD → Search Spec → Rubric (~3–4 days)

- [ ] `POST /api/jobs` — create role with JD text
- [ ] `POST /api/jobs/{id}/parse` — LLM mock returns SearchQuery JSON
- [ ] `PUT /api/jobs/{id}/search-spec` — recruiter edits and confirms
- [ ] `PUT /api/jobs/{id}/rubric` — recruiter sets weighted criteria + must-have filters
- [ ] `PUT /api/jobs/{id}/mode` — manual or auto with threshold
- [ ] Prompt file: `prompts/jd_parse/v1.txt`
- [ ] Screen: Job Setup (JD input, search spec editor, rubric editor, mode switch)

**Acceptance**: Paste a JD → see parsed spec → edit → confirm rubric → see mode switch.

---

### Step 3 — Sourcing Pipeline (~5–6 days)

- [ ] `POST /api/jobs/{id}/source` — enqueues sourcing Celery tasks
- [ ] GitHubAdapter: search users by skill keywords via GitHub REST API (unauthenticated)
- [ ] StackOverflowAdapter: search users via SO API v2.3 (no key)
- [ ] DuckDuckGoAdapter: search via `duckduckgo-search` library
- [ ] Entity resolution service: merge by name + employer + location + handle → confidence score
- [ ] Deduplication against existing pool
- [ ] Scoring service: 6 components, evidence snippets + source URLs per component
- [ ] `GET /api/jobs/{id}/sourcing-status` — SSE stream of live progress
- [ ] Screen: Sourcing Run (live progress per pool, counts, errors)

**Acceptance**: Trigger sourcing → watch live progress → see deduplicated, scored pool.

---

### Step 4 — Review UI (~3–4 days)

- [ ] `GET /api/jobs/{id}/candidates` — paginated, ranked, filterable
- [ ] `GET /api/jobs/{id}/candidates/{cid}/score` — full score breakdown with evidence
- [ ] `POST /api/jobs/{id}/candidates/export` — CSV export
- [ ] Screen: Candidate Pool (TanStack Table + virtualization, side evidence panel, bulk actions)

**Acceptance**: Browse ranked candidates → click any → see score components and evidence links → export CSV.

---

### Step 5 — Calibration (~4–5 days)

- [ ] `GET /api/jobs/{id}/calibration/batch` — returns next batch of 20–30 diverse profiles
- [ ] `POST /api/jobs/{id}/calibration/label` — stores Yes/No/Maybe + reason tags
- [ ] `POST /api/jobs/{id}/calibration/rerank` — re-ranks pool using label signals
- [ ] Preference model v1: mock embedding similarity (placeholder ranker using score components)
- [ ] `GET /api/jobs/{id}/preferences` — plain-language preferences from mock LLM
- [ ] `PUT /api/jobs/{id}/preferences/{id}` — edit or remove a learned preference
- [ ] Screen: Calibration Deck (card stack, Y/N/M keys, reason tags, yes-rate, batch progress)
- [ ] Screen: What I've Learned (preferences list with confirm/edit/remove)

**Acceptance**: Label 20 profiles → next batch appears → ranking visibly changes → What I've Learned panel updates.

---

### Step 6 — Rules and Dashboard (~3–4 days)

- [ ] `POST /api/jobs/{id}/rules` — parse NL rule → structured rule + plain preview (mock LLM)
- [ ] `PUT /api/jobs/{id}/rules/{rid}/confirm` — activate rule
- [ ] `GET /api/jobs/{id}/dashboard` — shortlisted candidates with which rule admitted each
- [ ] Screen: Rule Builder (NL input → structured preview → confirm)
- [ ] Screen: Role Dashboard (shortlisted, rule column, screening + interview status)
- [ ] Prompt files: `prompts/rule_parse/v1.txt`, `prompts/rule_preview/v1.txt`

**Acceptance**: Type "resume score at least 75" → see structured rule → confirm → dashboard shows matching candidates with rule column.

---

### Step 7 — Outreach, Screening, Interview (all mock) (~4–5 days)

- [ ] `POST /api/jobs/{id}/candidates/{cid}/outreach` — enqueues outreach task
- [ ] MockOutreachAdapter: simulates WhatsApp send + reply after configured delay
- [ ] MockOutreachAdapter: simulates email send + reply after configured delay
- [ ] MockTelephonyAdapter: simulates AI phone screen + transcript after delay
- [ ] MockInterviewAdapter: simulates AI technical interview + scores after delay
- [ ] Escalation scheduler: checks for no-reply after 48h → triggers next channel
- [ ] Interview gate: only candidates with answers who meet role filters
- [ ] `GET /api/jobs/{id}/candidates/{cid}/timeline` — full outreach history
- [ ] `POST /api/jobs/{id}/candidates/{cid}/move-to-interview` — recruiter action only
- [ ] Screen: Outreach Timeline (messages, replies, phone attempts, interview transcript)
- [ ] Screen: Pipeline Board (6 stages, counts per stage, drag to move within recruiter-allowed actions)
- [ ] Prompt files: `prompts/screening_questions/v1.txt`, `prompts/interview_questions/v1.txt`, `prompts/outreach_whatsapp/v1.txt`, `prompts/outreach_email/v1.txt`

**Acceptance**: Shortlist candidate → see WhatsApp mock sent → mock reply arrives → pipeline moves → AI interview runs → transcript appears → recruiter moves to Human Interview.

---

### Step 8 — Compliance and Settings (~3–4 days)

- [ ] Suppression list enforcement: check before every outreach + enrichment
- [ ] `POST /api/candidates/{cid}/opt-out` — adds to suppression list, stops all outreach
- [ ] Contact reveal endpoint: logs audit entry, requires `reveal_contact` permission
- [ ] `GET /api/audit-log` — filterable by user, date, action type
- [ ] Screen: Audit Log
- [ ] Screen: Settings (API keys per workspace, credit budgets, retention, user roles)
- [ ] Retention sweep scheduler: redacts PII past retention date

**Acceptance**: Opt out a candidate → they never appear again → audit log shows all actions → settings screen saves workspace config.

---

### Step 9 — Tests (~3–4 days)

**pytest (backend):**
- [ ] JD parsing (mock returns correct SearchQuery shape)
- [ ] Query generation (search spec → adapter query params)
- [ ] Entity resolution (same person from two sources → merged; different people → not merged)
- [ ] Scoring (all 6 components present; protected attributes absent from inputs)
- [ ] Suppression (suppressed candidate never appears in results)
- [ ] Label storage (Yes/No/Maybe stored with correct batch number)
- [ ] Re-ranking (after Yes labels, those profiles rank higher)
- [ ] One-sided labels (all No → cold-start guard triggers)
- [ ] Outreach escalation (no reply after 48h → next channel triggered)
- [ ] Interview gate (candidate without answers does not receive interview)
- [ ] Protected-attribute test (scoring service receives no name, photo, gender, age, religion, caste, nationality in feature inputs)
- [ ] Mock-recruiter simulation (labels from hidden target → yes-rate improves across 3 batches)

**Playwright (E2E):**
- [ ] Calibration deck: Y/N/M keyboard controls work; yes-rate updates; batch advances
- [ ] Rule builder: type NL rule → see preview → confirm → candidate appears on dashboard
- [ ] Outreach timeline: mock events appear in correct order with timestamps

---

## Phase 2 — Live Integrations

- Apollo.io / Juicebox contact adapter (Juicebox API key from dev team)
- Real LLM API (JD parsing, scoring, summaries, rule preview)
- Real embedding model (sentence-transformers or API)
- LLM query refinement (reads labels + reason tags → adjusts search spec)
- Active-learning batch selection (proper boundary + exploration sampling)
- Email verification via contact adapter
- Live WhatsApp sending via Gupshup
- Live email sending via authenticated domain
- Live AI phone screen via Plivo
- Live AI technical interview via Plivo / TBD
- Credit budget enforcement with per-workspace alerts
- Coverage report by provider
- ATS / CRM export adapters

---

## Phase 3 — Scale and Multi-Tenancy

- More sourcing adapters (LinkedIn Talent Solutions if approved, others)
- Reusable preference templates across roles
- Full multi-tenant workspace management
- Analytics dashboards (sourcing funnel, yes-rate trends, time-to-shortlist)
- Performance optimisation (HNSW indexes, read replicas, caching)
- Production infrastructure (cloud hosting, India data residency)
