"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type AuditEntry } from "@/lib/api";
import {
  FileText,
  ChevronLeft, ChevronRight, ChevronDown, ChevronUp,
} from "lucide-react";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString("en-GB", {
    day: "numeric", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function truncateId(id: string | null) {
  if (!id) return "—";
  return id.length > 12 ? `${id.slice(0, 8)}…` : id;
}

export default function AuditPage() {
  const { id } = useParams<{ id: string }>();
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    api.listAuditLog(page)
      .then(setEntries)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page]);

  return (
    <main className="max-w-5xl mx-auto px-6 pb-10">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-slate-200">Audit Log</h2>
        <div className="flex items-center gap-2">
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
            disabled={entries.length < 50}
            className="p-1.5 rounded hover:bg-slate-800 disabled:opacity-30 transition-colors"
          >
            <ChevronRight size={16} className="text-slate-300" />
          </button>
        </div>
      </div>

      {loading && <p className="text-slate-400 text-sm">Loading…</p>}

      {!loading && entries.length === 0 && (
        <div className="surface p-10 text-center">
          <FileText size={32} className="text-slate-700 mx-auto mb-3" />
          <p className="text-slate-400 text-sm">No audit events yet.</p>
        </div>
      )}

      {!loading && entries.length > 0 && (
        <div className="surface overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-xs text-slate-400">
                <th className="text-left px-4 py-3">Time</th>
                <th className="text-left px-4 py-3">Action</th>
                <th className="text-left px-4 py-3">Entity</th>
                <th className="text-left px-4 py-3">ID</th>
                <th className="px-4 py-3 w-8" />
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => (
                <>
                  <tr
                    key={entry.id}
                    onClick={() => setExpanded(expanded === entry.id ? null : entry.id)}
                    className="border-b border-slate-800/50 cursor-pointer hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">{formatDate(entry.created_at)}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded bg-slate-700 text-xs font-mono text-teal-light">{entry.action}</span>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-300">{entry.entity_type ?? "—"}</td>
                    <td className="px-4 py-3 text-xs font-mono text-slate-500" title={entry.entity_id ?? ""}>
                      {truncateId(entry.entity_id)}
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {expanded === entry.id ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                    </td>
                  </tr>
                  {expanded === entry.id && (
                    <tr key={`${entry.id}-detail`} className="border-b border-slate-800/50 bg-slate-900/50">
                      <td colSpan={5} className="px-4 py-3">
                        <pre className="text-xs text-slate-300 font-mono overflow-x-auto whitespace-pre-wrap break-all">
                          {JSON.stringify(entry.detail, null, 2)}
                        </pre>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
