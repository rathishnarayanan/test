"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type CandidateRow } from "@/lib/api";
import { Info } from "lucide-react";

const COLUMNS = [
  { key: "shortlisted", label: "Shortlisted", color: "text-teal-light" },
  { key: "contacted", label: "Contacted", color: "text-amber-DEFAULT" },
  { key: "screened", label: "Screened", color: "text-teal-DEFAULT" },
  { key: "technical", label: "Technical", color: "text-purple-400" },
  { key: "ready", label: "Ready", color: "text-emerald-400" },
  { key: "decided", label: "Decided", color: "text-slate-400" },
];

function scoreColor(s: number) {
  if (s >= 80) return "text-teal-light";
  if (s >= 60) return "text-amber-DEFAULT";
  return "text-slate-400";
}

export default function PipelinePage() {
  const { id } = useParams<{ id: string }>();
  const [candidates, setCandidates] = useState<CandidateRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listCandidates(id)
      .then(setCandidates)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  const buckets: Record<string, CandidateRow[]> = {
    shortlisted: candidates,
    contacted: [],
    screened: [],
    technical: [],
    ready: [],
    decided: [],
  };

  return (
    <main className="max-w-7xl mx-auto px-6 pb-10">
      {loading && <p className="text-slate-400">Loading…</p>}

      {!loading && (
        <>
          <div className="overflow-x-auto pb-4">
            <div className="flex gap-3 min-w-max">
              {COLUMNS.map((col) => (
                <div key={col.key} className="w-56 shrink-0">
                  <div className="flex items-center justify-between mb-2 px-1">
                    <span className={`text-xs font-semibold ${col.color}`}>{col.label}</span>
                    <span className="text-xs font-mono text-slate-500">{buckets[col.key].length}</span>
                  </div>
                  <div className="space-y-2">
                    {buckets[col.key].length === 0 && (
                      <div className="surface p-3 text-center">
                        <p className="text-xs text-slate-600">Empty</p>
                      </div>
                    )}
                    {buckets[col.key].map((c) => (
                      <div key={c.id} className="surface p-3 space-y-1">
                        <p className="text-sm font-medium text-slate-100 truncate">{c.full_name}</p>
                        <p className="text-xs text-slate-400 truncate">{c.current_title ?? "—"}</p>
                        <div className="flex items-center justify-between mt-1">
                          <div className="flex flex-wrap gap-1">
                            {c.skills.slice(0, 2).map((s) => (
                              <span key={s} className="px-1.5 py-0.5 rounded bg-slate-700 text-xs text-slate-400">{s}</span>
                            ))}
                          </div>
                          <span className={`font-mono text-sm font-semibold ${scoreColor(c.total_score)}`}>
                            {Math.round(c.total_score)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 flex items-start gap-2 text-xs text-slate-500">
            <Info size={12} className="mt-0.5 shrink-0" />
            <p>Full pipeline status requires outreach events (Phase 1: all candidates shown in Shortlisted).</p>
          </div>
        </>
      )}
    </main>
  );
}
