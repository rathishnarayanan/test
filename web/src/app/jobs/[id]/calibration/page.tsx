"use client";
import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import {
  api, type CalibrationBatch, type CalibrationCard,
} from "@/lib/api";
import {
  AlertTriangle, CheckCircle, XCircle, HelpCircle,
} from "lucide-react";

const REASON_TAGS = [
  "wrong_seniority", "wrong_domain", "location_mismatch",
  "missing_skills", "overqualified", "poor_profile",
];

export default function CalibrationPage() {
  const { id } = useParams<{ id: string }>();
  const [batch, setBatch] = useState<CalibrationBatch | null>(null);
  const [batchNumber, setBatchNumber] = useState(1);
  const [cardIndex, setCardIndex] = useState(0);
  const [yesRate, setYesRate] = useState(0);
  const [awaitingTags, setAwaitingTags] = useState<"no" | "maybe" | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [reranking, setReranking] = useState(false);

  const loadBatch = useCallback(() => {
    setLoading(true);
    api.getCalibrationBatch(id, batchNumber)
      .then((b) => {
        setBatch(b);
        setYesRate(b.yes_rate);
        setCardIndex(0);
        setAwaitingTags(null);
        setSelectedTags([]);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id, batchNumber]);

  useEffect(() => { loadBatch(); }, [loadBatch]);

  const card: CalibrationCard | undefined = batch?.batch[cardIndex];

  async function applyLabel(label: "yes" | "no" | "maybe", tags: string[]) {
    if (!card) return;
    try {
      const res = await api.applyLabel(id, {
        candidate_id: card.candidate_id,
        label,
        reason_tags: tags,
        batch_number: batchNumber,
      });
      setYesRate(res.yes_rate);
      setAwaitingTags(null);
      setSelectedTags([]);
      setCardIndex((i) => i + 1);
    } catch (e) {
      console.error(e);
    }
  }

  function handleLabel(label: "yes" | "no" | "maybe") {
    if (label === "yes") {
      applyLabel("yes", []);
    } else {
      setAwaitingTags(label);
    }
  }

  function confirmTags() {
    if (awaitingTags) applyLabel(awaitingTags, selectedTags);
  }

  function toggleTag(tag: string) {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  }

  async function handleRerank() {
    setReranking(true);
    try {
      await api.rerank(id);
      setBatchNumber((n) => n + 1);
    } catch (e) {
      console.error(e);
    } finally {
      setReranking(false);
    }
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (awaitingTags) return;
      if (!card) return;
      if (e.key === "y" || e.key === "Y") handleLabel("yes");
      if (e.key === "n" || e.key === "N") handleLabel("no");
      if (e.key === "m" || e.key === "M") handleLabel("maybe");
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [card, awaitingTags]);

  const batchDone = batch && cardIndex >= batch.batch.length;

  return (
    <main className="max-w-5xl mx-auto px-6 pb-10">
      {/* Yes-rate bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-slate-400 mb-1">
          <span>Yes rate</span>
          <span className="font-mono text-teal-light">{Math.round(yesRate * 100)}%</span>
        </div>
        <div className="h-2 rounded bg-slate-800 overflow-hidden">
          <div className="h-full rounded bg-teal-DEFAULT transition-all" style={{ width: `${yesRate * 100}%` }} />
        </div>
      </div>

      {loading && <p className="text-slate-400">Loading batch…</p>}

      {!loading && batch?.cold_start.cold_start && (
        <div className="surface p-4 flex items-start gap-3 mb-6 border-amber-DEFAULT/40">
          <AlertTriangle size={16} className="text-amber-DEFAULT mt-0.5 shrink-0" />
          <div>
            <p className="text-sm text-amber-DEFAULT font-medium">Cold start</p>
            <p className="text-xs text-slate-400 mt-0.5">{batch.cold_start.suggestion ?? "Pool may be too small. Try broadening your JD."}</p>
          </div>
        </div>
      )}

      {!loading && batchDone && (
        <div className="surface p-8 text-center space-y-4">
          <p className="text-slate-300">Batch {batchNumber} complete.</p>
          <button
            onClick={handleRerank}
            disabled={reranking}
            className="px-5 py-2.5 rounded bg-teal-DEFAULT hover:bg-teal-dark disabled:opacity-50 text-white text-sm transition-colors"
          >
            {reranking ? "Re-ranking…" : "Re-rank & get next batch"}
          </button>
        </div>
      )}

      {!loading && card && !batchDone && (
        <div className="space-y-5">
          {/* Progress */}
          <p className="text-xs text-slate-400 font-mono">
            {cardIndex + 1} / {batch?.batch.length} — Batch {batchNumber}
          </p>

          {/* Card */}
          <div className="surface p-6 space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-100">{card.full_name}</h2>
                <p className="text-sm text-slate-400">{card.current_title ?? "—"} · {card.current_employer ?? "—"}</p>
                {card.location && <p className="text-xs text-slate-500 mt-0.5">{card.location}</p>}
              </div>
              <span className={`font-mono text-lg font-bold ${card.total_score >= 80 ? "text-teal-light" : card.total_score >= 60 ? "text-amber-DEFAULT" : "text-slate-400"}`}>
                {Math.round(card.total_score)}
              </span>
            </div>

            {card.skills.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {card.skills.slice(0, 5).map((s) => (
                  <span key={s} className="px-2 py-0.5 rounded bg-slate-700 text-xs text-slate-300">{s}</span>
                ))}
              </div>
            )}

            {/* Score components mini */}
            <div className="space-y-1.5">
              {Object.entries(card.components).map(([name, comp]) => (
                <div key={name} className="flex items-center gap-2 text-xs">
                  <span className="text-slate-400 w-28 capitalize">{name.replace(/_/g, " ")}</span>
                  <div className="flex-1 h-1.5 rounded bg-slate-700 overflow-hidden">
                    <div className="h-full rounded bg-teal-DEFAULT/70" style={{ width: `${comp.score * 100}%` }} />
                  </div>
                  <span className="font-mono text-slate-400 w-8 text-right">{Math.round(comp.score * 100)}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Reason tags */}
          {awaitingTags && (
            <div className="surface p-4 space-y-3">
              <p className="text-xs text-slate-400">Select reason tags (optional):</p>
              <div className="flex flex-wrap gap-2">
                {REASON_TAGS.map((tag) => (
                  <button
                    key={tag}
                    onClick={() => toggleTag(tag)}
                    className={`px-2.5 py-1 rounded text-xs transition-colors ${
                      selectedTags.includes(tag)
                        ? "bg-teal-DEFAULT text-white"
                        : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
              <button
                onClick={confirmTags}
                className="px-4 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-sm text-slate-200 transition-colors"
              >
                Confirm {awaitingTags}
              </button>
            </div>
          )}

          {/* Label buttons */}
          {!awaitingTags && (
            <div className="flex gap-3">
              <button
                onClick={() => handleLabel("yes")}
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded bg-emerald-900/40 hover:bg-emerald-900/70 border border-emerald-700/40 text-emerald-400 text-sm transition-colors"
              >
                <CheckCircle size={16} />
                Yes <span className="text-xs opacity-60">(Y)</span>
              </button>
              <button
                onClick={() => handleLabel("maybe")}
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded bg-amber-900/30 hover:bg-amber-900/60 border border-amber-700/40 text-amber-DEFAULT text-sm transition-colors"
              >
                <HelpCircle size={16} />
                Maybe <span className="text-xs opacity-60">(M)</span>
              </button>
              <button
                onClick={() => handleLabel("no")}
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded bg-rose-900/30 hover:bg-rose-900/60 border border-rose-700/40 text-rose-DEFAULT text-sm transition-colors"
              >
                <XCircle size={16} />
                No <span className="text-xs opacity-60">(N)</span>
              </button>
            </div>
          )}
        </div>
      )}
    </main>
  );
}
