"use client";
import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  api, type CandidateRow, type ScoreDetail, type RevealResult,
} from "@/lib/api";
import {
  X, Download, ChevronLeft, ChevronRight, ExternalLink,
} from "lucide-react";

const REASON_TAGS = [
  "wrong_seniority", "wrong_domain", "location_mismatch",
  "missing_skills", "overqualified", "poor_profile",
];

function scoreColor(s: number) {
  if (s >= 80) return "text-teal-light";
  if (s >= 60) return "text-amber-DEFAULT";
  return "text-slate-400";
}

export default function CandidatesPage() {
  const { id } = useParams<{ id: string }>();
  const [candidates, setCandidates] = useState<CandidateRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [minScore, setMinScore] = useState(0);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<CandidateRow | null>(null);
  const [scoreDetail, setScoreDetail] = useState<ScoreDetail | null>(null);
  const [scoreLoading, setScoreLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState<string | null>(null);
  const [revealed, setRevealed] = useState<RevealResult | null>(null);
  const [suppressConfirm, setSuppressConfirm] = useState(false);

  const loadCandidates = useCallback(() => {
    setLoading(true);
    api.listCandidates(id, page, minScore)
      .then(setCandidates)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id, page, minScore]);

  useEffect(() => { loadCandidates(); }, [loadCandidates]);

  async function openDetail(c: CandidateRow) {
    setSelected(c);
    setScoreDetail(null);
    setActionMsg(null);
    setRevealed(null);
    setSuppressConfirm(false);
    setScoreLoading(true);
    try {
      const d = await api.getScore(id, c.id);
      setScoreDetail(d);
    } catch {
      // score may not exist yet
    } finally {
      setScoreLoading(false);
    }
  }

  async function handleOutreach() {
    if (!selected) return;
    try {
      await api.triggerOutreach(id, selected.id);
      setActionMsg("Outreach triggered.");
    } catch (e) {
      setActionMsg(String(e));
    }
  }

  async function handleInterview() {
    if (!selected) return;
    try {
      await api.moveToInterview(id, selected.id);
      setActionMsg("Moved to interview.");
    } catch (e) {
      setActionMsg(String(e));
    }
  }

  async function handleReveal() {
    if (!selected) return;
    try {
      const result = await api.revealContact(id, selected.id);
      setRevealed(result);
      setActionMsg(null);
    } catch (e) {
      setActionMsg(String(e));
    }
  }

  async function handleSuppress() {
    if (!selected) return;
    try {
      await api.suppressCandidate(id, selected.id);
      setSelected(null);
      setSuppressConfirm(false);
      loadCandidates();
    } catch (e) {
      setActionMsg(String(e));
    }
  }

  const filtered = candidates.filter((c) =>
    c.full_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <main className="max-w-7xl mx-auto px-6 pb-10">
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 mb-4">
        <input
          type="text"
          placeholder="Search by name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-DEFAULT w-56"
        />
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Min score:</span>
          <input
            type="range" min={0} max={100} value={minScore}
            onChange={(e) => { setMinScore(Number(e.target.value)); setPage(1); }}
            className="w-28 accent-teal-DEFAULT"
          />
          <span className="text-xs text-slate-300 font-mono w-6">{minScore}</span>
        </div>
        <button
          onClick={() => { window.location.href = `/api/jobs/${id}/candidates/export`; }}
          className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded bg-slate-800 hover:bg-slate-700 text-sm text-slate-200 transition-colors"
        >
          <Download size={14} />
          Export CSV
        </button>
      </div>

      {/* Table */}
      <div className="surface overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-800 text-xs text-slate-400">
              <th className="text-left px-4 py-3">Name</th>
              <th className="text-left px-4 py-3">Title</th>
              <th className="text-left px-4 py-3">Employer</th>
              <th className="text-left px-4 py-3">Location</th>
              <th className="text-left px-4 py-3">Skills</th>
              <th className="text-right px-4 py-3">Score</th>
              <th className="text-left px-4 py-3">Sources</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={7} className="text-center text-slate-400 py-10">Loading…</td></tr>
            )}
            {!loading && filtered.length === 0 && (
              <tr><td colSpan={7} className="text-center text-slate-400 py-10">No candidates found.</td></tr>
            )}
            {filtered.map((c) => (
              <tr
                key={c.id}
                onClick={() => openDetail(c)}
                className={`border-b border-slate-800/50 cursor-pointer hover:bg-slate-800/40 transition-colors ${selected?.id === c.id ? "bg-slate-800/60" : ""}`}
              >
                <td className="px-4 py-3 text-slate-100 font-medium">{c.full_name}</td>
                <td className="px-4 py-3 text-slate-300">{c.current_title ?? "—"}</td>
                <td className="px-4 py-3 text-slate-300">{c.current_employer ?? "—"}</td>
                <td className="px-4 py-3 text-slate-400">{c.location ?? "—"}</td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {c.skills.slice(0, 4).map((s) => (
                      <span key={s} className="px-1.5 py-0.5 rounded bg-slate-700 text-xs text-slate-300">{s}</span>
                    ))}
                    {c.skills.length > 4 && (
                      <span className="text-xs text-slate-500">+{c.skills.length - 4}</span>
                    )}
                  </div>
                </td>
                <td className={`px-4 py-3 text-right font-mono font-semibold ${scoreColor(c.total_score)}`}>
                  {Math.round(c.total_score)}
                </td>
                <td className="px-4 py-3 text-xs text-slate-400">{c.source_names.join(", ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-end gap-2 mt-3">
        <button
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
          className="p-1.5 rounded hover:bg-slate-800 disabled:opacity-30 transition-colors"
        >
          <ChevronLeft size={16} className="text-slate-300" />
        </button>
        <span className="text-xs text-slate-400">Page {page}</span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={filtered.length < 50}
          className="p-1.5 rounded hover:bg-slate-800 disabled:opacity-30 transition-colors"
        >
          <ChevronRight size={16} className="text-slate-300" />
        </button>
      </div>

      {/* Side panel */}
      {selected && (
        <div className="fixed inset-y-0 right-0 w-96 bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col z-50 overflow-y-auto">
          <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
            <div>
              <p className="font-semibold text-slate-100">{selected.full_name}</p>
              <p className="text-xs text-slate-400">{selected.current_title ?? "—"}</p>
            </div>
            <button onClick={() => setSelected(null)} className="p-1 rounded hover:bg-slate-800">
              <X size={16} className="text-slate-400" />
            </button>
          </div>

          <div className="flex-1 px-5 py-4 space-y-4">
            {/* Profile links */}
            {Object.entries(selected.profile_urls).length > 0 && (
              <div className="flex gap-2 flex-wrap">
                {Object.entries(selected.profile_urls).map(([k, v]) => (
                  <a key={k} href={v} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-1 text-xs text-teal-light hover:underline">
                    {k} <ExternalLink size={10} />
                  </a>
                ))}
              </div>
            )}

            {/* Score detail */}
            {scoreLoading && <p className="text-slate-400 text-sm">Loading score…</p>}
            {scoreDetail && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Total score</span>
                  <span className={`font-mono font-semibold ${scoreColor(scoreDetail.total_score)}`}>
                    {Math.round(scoreDetail.total_score)}
                  </span>
                </div>
                {Object.entries(scoreDetail.components).map(([name, comp]) => (
                  <div key={name}>
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-300 capitalize">{name.replace(/_/g, " ")}</span>
                      <span className="font-mono text-teal-light">{Math.round(comp.score * 100)}%</span>
                    </div>
                    <div className="h-1.5 rounded bg-slate-700 overflow-hidden">
                      <div
                        className="h-full rounded bg-teal-DEFAULT transition-all"
                        style={{ width: `${comp.score * 100}%` }}
                      />
                    </div>
                    {comp.evidence.length > 0 && (
                      <div className="mt-1 space-y-0.5">
                        {comp.evidence.slice(0, 2).map((ev, i) => (
                          <p key={i} className="text-xs text-slate-400 truncate">
                            {ev.url ? (
                              <a href={ev.url} target="_blank" rel="noopener noreferrer" className="hover:text-teal-light">
                                {ev.text}
                              </a>
                            ) : ev.text}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Reveal contact */}
            {!revealed ? (
              <button
                onClick={handleReveal}
                className="w-full py-2 rounded bg-slate-800 hover:bg-slate-700 text-sm text-slate-200 transition-colors"
              >
                Reveal Contact
              </button>
            ) : (
              <div className="rounded bg-slate-800 px-3 py-2 text-xs space-y-1">
                {revealed.email && <p className="text-slate-200 font-mono">{revealed.email}</p>}
                {revealed.phone && <p className="text-slate-200 font-mono">{revealed.phone}</p>}
                {!revealed.email && !revealed.phone && <p className="text-slate-400">No contact info available</p>}
              </div>
            )}

            {actionMsg && <p className="text-xs text-teal-light">{actionMsg}</p>}

            {suppressConfirm ? (
              <div className="space-y-1">
                <p className="text-xs text-slate-400">Suppress this candidate? They will never appear again.</p>
                <div className="flex gap-2">
                  <button
                    onClick={handleSuppress}
                    className="flex-1 py-1.5 rounded bg-rose-700 hover:bg-rose-600 text-white text-xs transition-colors"
                  >
                    Yes, suppress
                  </button>
                  <button
                    onClick={() => setSuppressConfirm(false)}
                    className="flex-1 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setSuppressConfirm(true)}
                className="w-full py-2 rounded bg-slate-800 hover:bg-slate-700 text-sm text-slate-400 transition-colors"
              >
                Suppress Candidate
              </button>
            )}
          </div>

          <div className="px-5 py-4 border-t border-slate-800 space-y-2">
            <button
              onClick={handleOutreach}
              className="w-full py-2 rounded bg-slate-800 hover:bg-slate-700 text-sm text-slate-200 transition-colors"
            >
              Trigger Outreach
            </button>
            <button
              onClick={handleInterview}
              className="w-full py-2 rounded bg-teal-DEFAULT hover:bg-teal-dark text-white text-sm transition-colors"
            >
              Move to Interview
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
