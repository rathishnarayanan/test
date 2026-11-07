# Data Model

All client tables are row-level secured by `workspace_id`. Platform tables are owned by the platform and read-only for all workspaces.

---

## Platform Schema

### `platform_candidates`
Shared read-only pool owned by the platform. No workspace_id — all workspaces can query it but cannot write.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| full_name | TEXT | |
| current_title | TEXT | |
| current_employer | TEXT | |
| location | TEXT | city, country |
| skills | TEXT[] | normalised skill tags |
| profile_urls | JSONB | `{"github": "...", "stackoverflow": "...", "web": [...]}` |
| raw_sources | JSONB | array of source records before merge |
| embedding | vector(768) | pgvector; mock (zeros) in Phase 1 |
| source_names | TEXT[] | which adapters contributed |
| last_seen_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | |

---

## Client Schema (workspace-scoped)

### `workspaces`

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| name | TEXT | |
| slug | TEXT UNIQUE | |
| settings | JSONB | retention_days, contact_reveal_enabled, budget_credits |
| created_at | TIMESTAMPTZ | |

### `users`

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | |
| email | TEXT UNIQUE | |
| role | TEXT | `admin`, `recruiter`, `viewer` |
| password_hash | TEXT | bcrypt |
| created_at | TIMESTAMPTZ | |

### `roles` (job descriptions)

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS |
| title | TEXT | |
| jd_text | TEXT | original job description |
| search_spec | JSONB | `{titles, skills_must, skills_nice, location, exclusions}` |
| rubric | JSONB | `{criteria: [{name, weight, must_have}], ...}` |
| mode | TEXT | `manual` or `auto` |
| auto_threshold | FLOAT | null if manual |
| status | TEXT | `draft`, `sourcing`, `calibrating`, `shortlisting`, `outreach`, `closed` |
| created_by | UUID FK users | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### `candidates`
Client-specific deduplicated profiles. May reference a `platform_candidates` record.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS |
| platform_candidate_id | UUID nullable | FK platform_candidates |
| full_name | TEXT | |
| current_title | TEXT | |
| current_employer | TEXT | |
| location | TEXT | |
| skills | TEXT[] | |
| profile_urls | JSONB | |
| email_masked | TEXT | `r***@example.com` |
| phone_masked | TEXT | `+91 ****5678` |
| email_revealed | TEXT | encrypted at rest; null until revealed |
| phone_revealed | TEXT | encrypted at rest; null until revealed |
| source_names | TEXT[] | |
| raw_sources | JSONB | |
| embedding | vector(768) | |
| suppressed | BOOLEAN | default false |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### `candidate_sources`
One row per raw source record before deduplication.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| candidate_id | UUID FK candidates | |
| workspace_id | UUID FK workspaces | RLS |
| adapter_name | TEXT | `github`, `stackoverflow`, `mock`, etc. |
| source_url | TEXT | |
| raw_data | JSONB | raw profile from adapter |
| fetched_at | TIMESTAMPTZ | |

### `scores`

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS |
| role_id | UUID FK roles | |
| candidate_id | UUID FK candidates | |
| total_score | FLOAT | 0–100 |
| components | JSONB | `{primary_skill, secondary_skill, experience, domain, location, recency}` each with score + evidence array |
| preference_model_version | TEXT | null until after first calibration |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### `labels`
Recruiter calibration events.

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS |
| role_id | UUID FK roles | |
| candidate_id | UUID FK candidates | |
| user_id | UUID FK users | |
| label | TEXT | `yes`, `no`, `maybe` |
| reason_tags | TEXT[] | e.g. `["overqualified", "wrong_stack"]` |
| batch_number | INT | calibration round |
| created_at | TIMESTAMPTZ | |

### `preference_model_versions`

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS |
| role_id | UUID FK roles | |
| version | INT | auto-increment per role |
| features | JSONB | model weights and learned criteria |
| yes_rate | FLOAT | yes-rate at time of creation |
| label_counts | JSONB | `{yes, no, maybe}` |
| created_at | TIMESTAMPTZ | |

### `rules`

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS |
| role_id | UUID FK roles | |
| name | TEXT | human-readable label |
| natural_language | TEXT | what the recruiter typed |
| structured | JSONB | `{field, operator, value}` parsed rule |
| plain_preview | TEXT | LLM-generated plain-language description |
| confirmed | BOOLEAN | false until recruiter confirms |
| active | BOOLEAN | |
| created_by | UUID FK users | |
| created_at | TIMESTAMPTZ | |

### `outreach_events`

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS |
| role_id | UUID FK roles | |
| candidate_id | UUID FK candidates | |
| event_type | TEXT | `shortlist_notice`, `whatsapp_sent`, `email_sent`, `phone_attempted`, `interview_started`, `reply_received`, `opt_out` |
| channel | TEXT | `whatsapp`, `email`, `phone`, `interview` |
| direction | TEXT | `outbound`, `inbound` |
| content | TEXT | message body or transcript excerpt |
| status | TEXT | `sent`, `delivered`, `replied`, `failed`, `opted_out` |
| adapter_name | TEXT | which adapter sent/received |
| created_at | TIMESTAMPTZ | |

### `suppression_list`

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS (platform-wide suppression in separate table) |
| email_hash | TEXT | SHA-256 of email; enables check without storing PII |
| phone_hash | TEXT | SHA-256 of phone |
| reason | TEXT | `opt_out`, `manual`, `deletion_request` |
| created_at | TIMESTAMPTZ | |

### `audit_log`

| Column | Type | Notes |
|---|---|---|
| id | UUID PK | |
| workspace_id | UUID FK workspaces | RLS |
| user_id | UUID FK users nullable | null for system actions |
| action | TEXT | `contact_revealed`, `candidate_deleted`, `label_applied`, `rule_confirmed`, `outreach_sent`, `data_exported` |
| entity_type | TEXT | `candidate`, `role`, `rule`, etc. |
| entity_id | UUID | |
| detail | JSONB | action-specific metadata |
| created_at | TIMESTAMPTZ | |

---

## Indexes

```sql
-- Sourcing / scoring
CREATE INDEX ON candidates(workspace_id, suppressed);
CREATE INDEX ON scores(workspace_id, role_id, total_score DESC);
CREATE INDEX ON labels(workspace_id, role_id, batch_number);

-- Outreach
CREATE INDEX ON outreach_events(workspace_id, role_id, candidate_id);
CREATE INDEX ON outreach_events(workspace_id, event_type, created_at);

-- Suppression check (fast hash lookup)
CREATE INDEX ON suppression_list(workspace_id, email_hash);
CREATE INDEX ON suppression_list(workspace_id, phone_hash);

-- Embeddings (pgvector)
CREATE INDEX ON candidates USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON platform_candidates USING ivfflat (embedding vector_cosine_ops);

-- Audit
CREATE INDEX ON audit_log(workspace_id, created_at DESC);
CREATE INDEX ON audit_log(workspace_id, user_id, created_at DESC);
```

---

## Row-Level Security

```sql
-- Enable RLS on all workspace-scoped tables
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
-- (repeated for all client tables)

CREATE POLICY workspace_isolation ON candidates
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid);
```

The API sets `app.current_workspace_id` at the start of each request from the authenticated user's workspace.

---

## Retention and Deletion

- Retention period is configurable per workspace (`workspaces.settings.retention_days`); default is the shortest legally required.
- Deletion request: removes `email_revealed`, `phone_revealed`, `raw_sources` from `candidates`; marks as suppressed; writes audit entry; removes label influence from `preference_model_versions.features` where feasible.
- Labels and preference model versions follow the same retention schedule as the candidate record they relate to.
