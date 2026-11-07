"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { api, type Job, type SearchSpec } from "@/lib/api";
import {
  Briefcase, Settings, Users, BarChart2, Zap,
  MessageSquare, GitBranch, BookOpen, FileText, ChevronRight
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

export default function JobPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [parsing, setParsing] = useState(false);
  const [sourcing, setSourcing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    api.getJob(id).then(setJob).catch(() => router.push("/"));
  }, [id]);

  async function handleParse() {
    setParsing(true);
    try {
      const res = await api.parseJD(id);
      setJob((prev) => prev ? { ...prev, search_spec: res.search_spec } : prev);
      setMessage("JD parsed. Review the search spec below, then confirm sourcing.");
    } catch (e) {
      setMessage(String(e));
    } finally {
      setParsing(false);
    }
  }

  async function handleSource() {
    if (!job?.search_spec || !job?.rubric) {
      setMessage("Confirm search spec and rubric before sourcing.");
      return;
    }
    setSourcing(true);
    try {
      await api.triggerSourcing(id);
      setMessage("Sourcing started. Check the Candidates tab shortly.");
    } catch (e) {
      setMessage(String(e));
    } finally {
      setSourcing(false);
    }
  }

  if (!job) return <p className="text-slate-400 p-10">Loading…</p>;

  return (
    <main className="max-w-5xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Briefcase size={18} className="text-teal-DEFAULT" />
            <h1 className="text-xl font-semibold">{job.title}</h1>
          </div>
          <span className="font-mono text-xs text-slate-400">{job.status}</span>
        </div>
      </div>

      {/* Nav */}
      <div className="flex gap-1 mb-8 overflow-x-auto pb-1">
        {NAV.map(({ label, icon: Icon, href }) => (
          <Link
            key={label}
            href={`/jobs/${id}${href}`}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded text-sm text-slate-300 hover:text-teal-light hover:bg-slate-800 transition-colors whitespace-nowrap"
          >
            <Icon size={14} />
            {label}
          </Link>
        ))}
      </div>

      {/* Setup card */}
      <div className="space-y-5">
        {/* Step 1 */}
        <div className="surface p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-slate-200">1. Parse JD</h2>
            {job.search_spec && <span className="text-xs text-teal-light font-mono">confirmed</span>}
          </div>
          {!job.search_spec ? (
            <button
              onClick={handleParse}
              disabled={parsing}
              className="px-4 py-2 rounded bg-slate-800 hover:bg-slate-700 text-sm text-slate-200 transition-colors"
            >
              {parsing ? "Parsing…" : "Parse JD →"}
            </button>
          ) : (
            <div className="space-y-1">
              <p className="text-xs text-slate-400">Titles: <span className="text-slate-200">{job.search_spec.titles.join(", ")}</span></p>
              <p className="text-xs text-slate-400">Must-have: <span className="text-teal-light font-mono">{job.search_spec.skills_must.join(", ")}</span></p>
              <p className="text-xs text-slate-400">Nice-to-have: <span className="text-slate-300 font-mono">{job.search_spec.skills_nice.join(", ")}</span></p>
            </div>
          )}
        </div>

        {/* Step 2 */}
        <div className="surface p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-slate-200">2. Confirm Rubric</h2>
            {job.rubric && <span className="text-xs text-teal-light font-mono">confirmed</span>}
          </div>
          {job.rubric ? (
            <div className="space-y-1">
              {job.rubric.criteria.map((c) => (
                <div key={c.name} className="flex items-center gap-3 text-xs">
                  <span className="text-slate-400 w-32">{c.name}</span>
                  <span className="font-mono text-teal-light">{Math.round(c.weight * 100)}%</span>
                  {c.must_have && <span className="text-amber-DEFAULT">must-have</span>}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400">Default rubric will be used. Parse JD first.</p>
          )}
        </div>

        {/* Step 3 */}
        <div className="surface p-5">
          <h2 className="text-sm font-semibold text-slate-200 mb-3">3. Start Sourcing</h2>
          <button
            onClick={handleSource}
            disabled={sourcing || !job.search_spec}
            className="px-4 py-2 rounded bg-teal-DEFAULT hover:bg-teal-dark disabled:opacity-40 text-white text-sm transition-colors"
          >
            {sourcing ? "Starting…" : "Start sourcing"}
          </button>
          {!job.search_spec && (
            <p className="text-xs text-slate-500 mt-2">Parse JD first to enable sourcing.</p>
          )}
        </div>

        {message && (
          <p className="text-sm text-teal-light px-1">{message}</p>
        )}
      </div>
    </main>
  );
}
