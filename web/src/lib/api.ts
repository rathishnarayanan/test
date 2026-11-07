const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Jobs
  listJobs: () => request<Job[]>("/api/jobs"),
  getJob: (id: string) => request<Job>(`/api/jobs/${id}`),
  createJob: (body: { title: string; jd_text: string }) =>
    request<Job>("/api/jobs", { method: "POST", body: JSON.stringify(body) }),
  parseJD: (id: string) => request<{ search_spec: SearchSpec; mock: boolean }>(`/api/jobs/${id}/parse`, { method: "POST", body: "{}" }),
  updateSearchSpec: (id: string, spec: SearchSpec) =>
    request(`/api/jobs/${id}/search-spec`, { method: "PUT", body: JSON.stringify(spec) }),
  updateRubric: (id: string, rubric: Rubric) =>
    request(`/api/jobs/${id}/rubric`, { method: "PUT", body: JSON.stringify(rubric) }),
  updateMode: (id: string, mode: string, threshold?: number) =>
    request(`/api/jobs/${id}/mode`, { method: "PUT", body: JSON.stringify({ mode, auto_threshold: threshold }) }),
  triggerSourcing: (id: string) =>
    request(`/api/jobs/${id}/source`, { method: "POST", body: "{}" }),

  // Candidates
  listCandidates: (roleId: string, page = 1, minScore = 0) =>
    request<CandidateRow[]>(`/api/jobs/${roleId}/candidates?page=${page}&min_score=${minScore}`),
  getScore: (roleId: string, candidateId: string) =>
    request<ScoreDetail>(`/api/jobs/${roleId}/candidates/${candidateId}/score`),
  triggerOutreach: (roleId: string, candidateId: string) =>
    request(`/api/jobs/${roleId}/candidates/${candidateId}/outreach`, { method: "POST", body: "{}" }),
  moveToInterview: (roleId: string, candidateId: string) =>
    request(`/api/jobs/${roleId}/candidates/${candidateId}/move-to-interview`, { method: "POST", body: "{}" }),
  getTimeline: (roleId: string, candidateId: string) =>
    request<OutreachEvent[]>(`/api/jobs/${roleId}/candidates/${candidateId}/timeline`),
  revealContact: (roleId: string, candidateId: string) =>
    request<RevealResult>(`/api/jobs/${roleId}/candidates/${candidateId}/reveal`, { method: "POST", body: "{}" }),
  suppressCandidate: (roleId: string, candidateId: string) =>
    request<{ suppressed: boolean }>(`/api/jobs/${roleId}/candidates/${candidateId}/suppress`, { method: "POST", body: "{}" }),

  // Calibration
  getCalibrationBatch: (roleId: string, batchNumber = 1) =>
    request<CalibrationBatch>(`/api/jobs/${roleId}/calibration/batch?batch_number=${batchNumber}`),
  applyLabel: (roleId: string, body: LabelRequest) =>
    request<{ label: string; yes_rate: number }>(`/api/jobs/${roleId}/calibration/label`, { method: "POST", body: JSON.stringify(body) }),
  rerank: (roleId: string) =>
    request(`/api/jobs/${roleId}/calibration/rerank`, { method: "POST", body: "{}" }),

  // Rules
  listRules: (roleId: string) => request<RuleRow[]>(`/api/jobs/${roleId}/rules`),
  createRule: (roleId: string, natural_language: string) =>
    request<RuleRow>(`/api/jobs/${roleId}/rules`, { method: "POST", body: JSON.stringify({ natural_language }) }),
  confirmRule: (roleId: string, ruleId: string) =>
    request(`/api/jobs/${roleId}/rules/${ruleId}/confirm`, { method: "PUT", body: "{}" }),
  getDashboard: (roleId: string) =>
    request<Dashboard>(`/api/jobs/${roleId}/rules/dashboard`),

  // Preferences
  getPreferences: (roleId: string) => request<PreferencesResponse>(`/api/jobs/${roleId}/preferences`),
  updatePreference: (roleId: string, prefId: string, text: string) =>
    request(`/api/jobs/${roleId}/preferences/${prefId}`, { method: "PUT", body: JSON.stringify({ text }) }),
  removePreference: (roleId: string, prefId: string) =>
    request(`/api/jobs/${roleId}/preferences/${prefId}`, { method: "DELETE" }),

  // Audit
  listAuditLog: (page = 1) => request<AuditEntry[]>(`/api/audit?page=${page}`),

  // Settings
  getSettings: () => request<WorkspaceSettings>("/api/settings"),
  updateSettings: (body: Partial<WorkspaceSettings>) =>
    request<WorkspaceSettings>("/api/settings", { method: "PUT", body: JSON.stringify(body) }),
};

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Job {
  id: string;
  title: string;
  status: string;
  search_spec?: SearchSpec;
  rubric?: Rubric;
  mode?: string;
  auto_threshold?: number;
}

export interface SearchSpec {
  titles: string[];
  skills_must: string[];
  skills_nice: string[];
  location: string | null;
  exclusions: string[];
}

export interface Rubric {
  criteria: RubricCriterion[];
}

export interface RubricCriterion {
  name: string;
  weight: number;
  must_have: boolean;
}

export interface CandidateRow {
  id: string;
  full_name: string;
  current_title: string | null;
  current_employer: string | null;
  location: string | null;
  skills: string[];
  total_score: number;
  source_names: string[];
  profile_urls: Record<string, string>;
}

export interface ScoreComponent {
  score: number;
  weight: number;
  evidence: { text: string; url: string | null }[];
}

export interface ScoreDetail {
  candidate_id: string;
  total_score: number;
  components: Record<string, ScoreComponent>;
}

export interface CalibrationBatch {
  batch: CalibrationCard[];
  yes_rate: number;
  cold_start: { cold_start: boolean; reason?: string; suggestion?: string };
}

export interface CalibrationCard {
  candidate_id: string;
  full_name: string;
  current_title: string | null;
  current_employer: string | null;
  location: string | null;
  skills: string[];
  total_score: number;
  components: Record<string, ScoreComponent>;
  profile_urls: Record<string, string>;
}

export interface LabelRequest {
  candidate_id: string;
  label: "yes" | "no" | "maybe";
  reason_tags: string[];
  batch_number: number;
}

export interface RuleRow {
  id: string;
  natural_language: string;
  plain_preview: string | null;
  confirmed: boolean;
  active: boolean;
  structured?: Record<string, unknown>;
}

export interface Dashboard {
  shortlisted: ShortlistedCandidate[];
  rule_count: number;
}

export interface ShortlistedCandidate {
  candidate_id: string;
  full_name: string;
  current_title: string | null;
  total_score: number;
  admitted_by_rule: string;
  rule_id: string;
}

export interface PreferencesResponse {
  preferences: { id: string; text: string }[];
}

export interface OutreachEvent {
  id: string;
  event_type: string;
  channel: string | null;
  direction: string | null;
  content: string | null;
  status: string | null;
  adapter_name: string | null;
  created_at: string;
}

export interface AuditEntry {
  id: string;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  detail: Record<string, unknown>;
  created_at: string;
}

export interface RevealResult {
  email: string | null;
  phone: string | null;
  revealed: boolean;
}

export interface WorkspaceSettings {
  retention_days: number;
  contact_reveal_enabled: boolean;
  source_adapters: string[];
}
