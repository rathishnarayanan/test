# Architecture

## System Overview

Automatic Sourcing is an AI recruiting engine. A recruiter pastes a job description; the system finds candidates across public sources and the client's own database, scores them, contacts them, screens them, and surfaces a reviewed shortlist. The recruiter makes every final decision.

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Browser                                                        │
│  Next.js (TypeScript + Tailwind + Radix + TanStack)             │
│  Dark mode: review workspace  │  Light mode: client dashboard   │
└─────────────────┬───────────────────────────────────────────────┘
                  │ HTTPS / WebSocket (SSE for live progress)
┌─────────────────▼───────────────────────────────────────────────┐
│  API  (FastAPI, Python 3.12)                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ /jobs        │  │ /candidates  │  │ /outreach          │    │
│  │ /sourcing    │  │ /labels      │  │ /rules             │    │
│  │ /calibration │  │ /scores      │  │ /audit             │    │
│  └──────────────┘  └──────────────┘  └────────────────────┘    │
│  Adapter Registry                                               │
│  ┌────────────┬──────────────┬──────────────┬─────────────┐    │
│  │ sources    │ contact      │ llm          │ outreach    │    │
│  │ telephony  │ interview    │              │             │    │
│  └────────────┴──────────────┴──────────────┴─────────────┘    │
└──────┬──────────────────────────────────────────────────────────┘
       │ Celery tasks (Redis broker)
┌──────▼──────────────────────────────────────────────────────────┐
│  Worker  (Celery + Redis)                                       │
│  Sourcing jobs │ Scoring jobs │ Outreach jobs │ Interview jobs  │
└──────┬──────────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────────┐
│  Scheduler  (Celery Beat)                                       │
│  Escalation checks │ Retention sweeps │ Suppression syncs       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  PostgreSQL 16 + pgvector                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  platform schema (universal pool, shared read-only)     │    │
│  │  platform_candidates                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  client schema (row-level security by workspace_id)     │    │
│  │  workspaces, roles, candidates, scores, labels,         │    │
│  │  rules, outreach_events, suppression_list, audit_log    │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  Redis                                                           │
│  Celery broker + result backend │ SSE event streams              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Adapters (all Mock in Phase 1)

| Category | Interface | Phase 1 | Phase 2+ |
|---|---|---|---|
| Sources | `SourceAdapter` | Mock, GitHub API, Stack Overflow API, DuckDuckGo | Juicebox |
| Contact | `ContactAdapter` | Mock | Apollo.io, Juicebox |
| LLM | `LLMAdapter` | Mock (structured dummy JSON) | Real LLM API |
| WhatsApp | `OutreachAdapter` | Mock | Gupshup |
| Email | `OutreachAdapter` | Mock | SMTP / SendGrid |
| Telephony / AI phone | `TelephonyAdapter` | Mock | Plivo |
| AI interview | `InterviewAdapter` | Mock | Plivo / TBD |
| Embeddings | `EmbeddingAdapter` | Mock (random vectors) | sentence-transformers |

Adapter selection is controlled by environment variables. Swapping Mock → real is a one-line config change.

---

## Data Flow: JD → Shortlist

```
Recruiter pastes JD
        │
        ▼
LLMAdapter.complete("jd_parse") → SearchQuery (titles, skills, location, exclusions)
        │
        ▼
Recruiter confirms / edits SearchQuery
        │
        ▼
Recruiter confirms Rubric (weighted criteria + must-have filters)
        │
        ▼
Sourcing runs in parallel (Celery tasks):
  ├── GitHubAdapter.search(query)
  ├── StackOverflowAdapter.search(query)
  ├── DuckDuckGoAdapter.search(query)
  ├── MockSourceAdapter.search(query)
  └── platform_candidates (SQL query against universal pool)
        │
        ▼
Entity resolution → deduplicated candidate pool
        │
        ▼
Scoring (per rubric) → score + component breakdown + evidence snippets
        │
        ▼
Calibration deck (20–30 diverse profiles)
        │
        ▼
Recruiter labels Yes / No / Maybe
        │
        ▼
Re-ranking + query refinement → next batch
        │
        ▼
Full pool ranked → Rules applied → Shortlist
        │
        ▼
Outreach (WhatsApp mock → email mock → AI phone mock → AI interview mock)
        │
        ▼
Recruiter reviews evidence → moves to Human Interview
```

---

## Security Boundaries

- All API endpoints require authentication (JWT, role-based).
- Contact fields are masked by default; reveal is a logged action requiring `reveal_contact` permission.
- PII encrypted at rest (PostgreSQL column-level encryption for phone/email).
- Secrets in `.env` only; never hardcoded.
- Row-level security enforced at the database layer for all workspace-scoped tables.
- Platform candidates table: read-only for all workspaces; write only via platform admin role.

---

## Infrastructure (Phase 1 — local only)

```
docker compose up
  ├── db        (postgres:16 + pgvector extension)
  ├── redis     (redis:7)
  ├── api       (FastAPI, uvicorn, port 8000)
  ├── worker    (Celery, same image as api)
  ├── scheduler (Celery beat, same image as api)
  └── web       (Next.js, port 3000)
```
