"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type CandidateRow, type OutreachEvent } from "@/lib/api";
import {
  MessageSquare,
  Phone, Mail, CheckCircle, ArrowUpRight, ArrowDownLeft,
} from "lucide-react";

function eventIcon(type: string) {
  if (type.includes("phone") || type.includes("call")) return <Phone size={14} />;
  if (type.includes("email")) return <Mail size={14} />;
  if (type.includes("complete") || type.includes("success")) return <CheckCircle size={14} />;
  return <MessageSquare size={14} />;
}

function formatDate(iso: string) {
  const d = new Date(iso);
  return d.toLocaleString("en-GB", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function OutreachPage() {
  const { id } = useParams<{ id: string }>();
  const [candidates, setCandidates] = useState<CandidateRow[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [timeline, setTimeline] = useState<OutreachEvent[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);

  useEffect(() => { api.listCandidates(id).then(setCandidates).catch(console.error); }, [id]);

  async function selectCandidate(cid: string) {
    setSelectedId(cid);
    setTimeline([]);
    setTimelineLoading(true);
    try {
      const events = await api.getTimeline(id, cid);
      setTimeline(events);
    } catch {
      setTimeline([]);
    } finally {
      setTimelineLoading(false);
    }
  }

  const selectedCandidate = candidates.find((c) => c.id === selectedId);

  return (
    <main className="max-w-5xl mx-auto px-6 pb-10">
      <div className="flex gap-5 h-[600px]">
        {/* Sidebar */}
        <div className="w-56 shrink-0 surface overflow-y-auto">
          <p className="text-xs text-slate-400 px-3 py-2 border-b border-slate-800">Candidates</p>
          {candidates.length === 0 && (
            <p className="text-xs text-slate-500 px-3 py-4">No candidates yet.</p>
          )}
          {candidates.map((c) => (
            <button
              key={c.id}
              onClick={() => selectCandidate(c.id)}
              className={`w-full text-left px-3 py-2.5 text-sm transition-colors hover:bg-slate-800 border-b border-slate-800/40 last:border-0 ${selectedId === c.id ? "bg-slate-800 text-teal-light" : "text-slate-300"}`}
            >
              <p className="font-medium truncate">{c.full_name}</p>
              <p className="text-xs text-slate-500 truncate">{c.current_title ?? "—"}</p>
            </button>
          ))}
        </div>

        {/* Timeline */}
        <div className="flex-1 surface overflow-y-auto">
          {!selectedId && (
            <div className="flex items-center justify-center h-full">
              <p className="text-slate-400 text-sm">Select a candidate to view their outreach history.</p>
            </div>
          )}
          {selectedId && timelineLoading && (
            <div className="flex items-center justify-center h-full">
              <p className="text-slate-400 text-sm">Loading…</p>
            </div>
          )}
          {selectedId && !timelineLoading && timeline.length === 0 && (
            <div className="flex items-center justify-center h-full">
              <p className="text-slate-400 text-sm">No outreach events yet for {selectedCandidate?.full_name}.</p>
            </div>
          )}
          {selectedId && !timelineLoading && timeline.length > 0 && (
            <div className="p-4 space-y-1">
              <p className="text-sm font-medium text-slate-200 mb-4">{selectedCandidate?.full_name}</p>
              {timeline.map((ev, i) => (
                <div key={ev.id} className="flex gap-3">
                  {/* Spine */}
                  <div className="flex flex-col items-center">
                    <div className="mt-1 p-1.5 rounded-full bg-slate-800 text-slate-400">
                      {eventIcon(ev.event_type)}
                    </div>
                    {i < timeline.length - 1 && <div className="w-px flex-1 bg-slate-800 my-0.5" />}
                  </div>
                  {/* Content */}
                  <div className="pb-4 flex-1">
                    <div className="flex items-center flex-wrap gap-2 mb-1">
                      <span className="text-xs font-mono text-slate-300">{ev.event_type}</span>
                      {ev.direction && (
                        <span className={`flex items-center gap-0.5 text-xs px-1.5 py-0.5 rounded ${ev.direction === "OUT" ? "bg-teal-DEFAULT/20 text-teal-light" : "bg-slate-700 text-slate-300"}`}>
                          {ev.direction === "OUT" ? <ArrowUpRight size={10} /> : <ArrowDownLeft size={10} />}
                          {ev.direction}
                        </span>
                      )}
                      {ev.channel && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-slate-700 text-slate-400">{ev.channel}</span>
                      )}
                      {ev.status && (
                        <span className={`text-xs px-1.5 py-0.5 rounded font-mono ${ev.status === "delivered" || ev.status === "sent" ? "bg-emerald-900/30 text-emerald-400" : "bg-slate-700 text-slate-400"}`}>
                          {ev.status}
                        </span>
                      )}
                      <span className="ml-auto text-xs text-slate-500">{formatDate(ev.created_at)}</span>
                    </div>
                    {ev.content && (
                      <p className="text-sm text-slate-300 line-clamp-3">{ev.content}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
