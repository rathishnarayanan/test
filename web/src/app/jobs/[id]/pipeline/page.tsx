"use client";
import { useEffect, useState } from "react";
import { useParams, usePathname } from "next/navigation";
import Link from "next/link";
import { api, type CandidateRow, type Job } from "@/lib/api";
import {
  Briefcase, Settings, Users, BarChart2, Zap,
  MessageSquare, GitBranch, BookOpen, FileText, Info,
} from "lucide-react";

const NAV = [
  { label: "Setup", icon: Settings, href: "" },
  { label: "Candidates", icon: Users, href: "/candidates" },
  { label: "Calibration", icon: Zap, href: "/calibration" },
  { label: "Dashboard", icon: BarChart2, href: "/rules" },
  { label: "Outreach", icon: MessageSquare, href: "/outreach" },
  { label: "Pipeline", icon: GitBranch, href: "/pipeline" },
  { label: "Learned", icon: BookOpen, href: "/preferences" },
  { label: "Audit", icon: FileText, href: "/audit" },
];

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
  const pathname = usePathname();
  const [job, setJob] = useState<Job | null>(null);
  const [candidates, setCandidates] = useState<CandidateRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { api.getJob(id).then(setJob).catch(() => {}); }, [id]);
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
    <main className="max-w-7xl mx-auto px-6 py-10">
      <div className="flex items-center gap-2 mb-6">
        <Briefcase size={18} className="text-teal-DEFAULT" />
        <h1 className="text-xl font-semibold">{job?.title ?? id}</h1>
      </div>

      <div className="flex gap-1 mb-8 overflow-x-auto pb-1">
        {NAV.map(({ label, icon: Icon, href }) => {
          const active = pathname === `/jobs/${id}${href}`;
          return (
            <Link key={label} href={`/jobs/${id}${href}`}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition-colors whitespace-nowrap ${
                active ? "bg-slate-800 text-teal-light" : "text-slate-300 hover:text-teal-light hover:bg-slate-800"
              }`}
            >
              <Icon size={14} />{label}
            </Link>
          );
        })}
      </div>

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
