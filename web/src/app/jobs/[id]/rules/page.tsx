"use client";
import { useEffect, useState } from "react";
import { useParams, usePathname } from "next/navigation";
import Link from "next/link";
import { api, type RuleRow, type Dashboard, type Job } from "@/lib/api";
import {
  Briefcase, Settings, Users, BarChart2, Zap,
  MessageSquare, GitBranch, BookOpen, FileText,
  Plus, CheckCircle, Users2,
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

export default function RulesPage() {
  const { id } = useParams<{ id: string }>();
  const pathname = usePathname();
  const [job, setJob] = useState<Job | null>(null);
  const [rules, setRules] = useState<RuleRow[]>([]);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [nlInput, setNlInput] = useState("");
  const [pendingRule, setPendingRule] = useState<RuleRow | null>(null);
  const [adding, setAdding] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { api.getJob(id).then(setJob).catch(() => {}); }, [id]);

  useEffect(() => {
    api.listRules(id).then(setRules).catch(console.error);
    api.getDashboard(id).then(setDashboard).catch(console.error);
  }, [id]);

  async function handleAdd() {
    if (!nlInput.trim()) return;
    setAdding(true);
    setError(null);
    try {
      const rule = await api.createRule(id, nlInput.trim());
      setPendingRule(rule);
      setNlInput("");
    } catch (e) {
      setError(String(e));
    } finally {
      setAdding(false);
    }
  }

  async function handleConfirm() {
    if (!pendingRule) return;
    setConfirming(true);
    try {
      await api.confirmRule(id, pendingRule.id);
      setRules((prev) => [
        ...prev.filter((r) => r.id !== pendingRule.id),
        { ...pendingRule, confirmed: true, active: true },
      ]);
      setPendingRule(null);
      const dash = await api.getDashboard(id);
      setDashboard(dash);
    } catch (e) {
      setError(String(e));
    } finally {
      setConfirming(false);
    }
  }

  return (
    <main className="max-w-5xl mx-auto px-6 py-10">
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

      <div className="space-y-8">
        {/* Rule builder */}
        <div className="surface p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Rule Builder</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={nlInput}
              onChange={(e) => setNlInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleAdd(); }}
              placeholder="e.g. resume score ≥ 75 and has Python"
              className="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-DEFAULT"
            />
            <button
              onClick={handleAdd}
              disabled={adding || !nlInput.trim()}
              className="flex items-center gap-1.5 px-4 py-2 rounded bg-teal-DEFAULT hover:bg-teal-dark disabled:opacity-50 text-white text-sm transition-colors"
            >
              <Plus size={14} />
              {adding ? "Parsing…" : "Add rule"}
            </button>
          </div>
          {error && <p className="text-xs text-rose-DEFAULT">{error}</p>}

          {pendingRule && (
            <div className="bg-slate-800 rounded p-4 space-y-3">
              <div>
                <p className="text-xs text-slate-400 mb-1">Rule preview</p>
                <p className="text-sm text-slate-200 font-mono">{pendingRule.plain_preview ?? pendingRule.natural_language}</p>
              </div>
              <button
                onClick={handleConfirm}
                disabled={confirming}
                className="flex items-center gap-1.5 px-4 py-2 rounded bg-emerald-800 hover:bg-emerald-700 text-white text-sm transition-colors"
              >
                <CheckCircle size={14} />
                {confirming ? "Confirming…" : "Confirm & activate"}
              </button>
            </div>
          )}
        </div>

        {/* Rules list */}
        {rules.length > 0 && (
          <div className="surface p-5 space-y-3">
            <h2 className="text-sm font-semibold text-slate-200">Active Rules</h2>
            {rules.map((rule) => (
              <div key={rule.id} className="flex items-start justify-between gap-4 py-2 border-b border-slate-800/60 last:border-0">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-200">{rule.natural_language}</p>
                  {rule.plain_preview && (
                    <p className="text-xs text-slate-400 font-mono mt-0.5">{rule.plain_preview}</p>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className={`px-2 py-0.5 rounded text-xs font-mono ${rule.confirmed ? "bg-teal-DEFAULT/20 text-teal-light" : "bg-slate-700 text-slate-400"}`}>
                    {rule.confirmed ? "confirmed" : "pending"}
                  </span>
                  {rule.confirmed && (
                    <span className={`px-2 py-0.5 rounded text-xs font-mono ${rule.active ? "bg-emerald-900/40 text-emerald-400" : "bg-slate-700 text-slate-500"}`}>
                      {rule.active ? "active" : "inactive"}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Dashboard */}
        {dashboard && (
          <div className="space-y-4">
            <h2 className="text-sm font-semibold text-slate-200">Dashboard</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="surface p-4 flex items-center gap-3">
                <BarChart2 size={20} className="text-teal-DEFAULT" />
                <div>
                  <p className="text-xs text-slate-400">Rules</p>
                  <p className="text-2xl font-bold font-mono text-slate-100">{dashboard.rule_count}</p>
                </div>
              </div>
              <div className="surface p-4 flex items-center gap-3">
                <Users2 size={20} className="text-teal-DEFAULT" />
                <div>
                  <p className="text-xs text-slate-400">Shortlisted</p>
                  <p className="text-2xl font-bold font-mono text-slate-100">{dashboard.shortlisted.length}</p>
                </div>
              </div>
            </div>

            {dashboard.shortlisted.length > 0 && (
              <div className="surface overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-800 text-xs text-slate-400">
                      <th className="text-left px-4 py-3">Name</th>
                      <th className="text-right px-4 py-3">Score</th>
                      <th className="text-left px-4 py-3">Admitted by</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dashboard.shortlisted.map((c) => (
                      <tr key={c.candidate_id} className="border-b border-slate-800/50">
                        <td className="px-4 py-3 text-slate-100">{c.full_name}</td>
                        <td className="px-4 py-3 text-right font-mono text-teal-light">{Math.round(c.total_score)}</td>
                        <td className="px-4 py-3 text-xs text-slate-400 font-mono">{c.admitted_by_rule}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {dashboard.shortlisted.length === 0 && (
              <div className="surface p-8 text-center">
                <p className="text-slate-400 text-sm">No shortlisted candidates yet. Confirm and activate a rule.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
