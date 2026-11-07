"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import {
  BookOpen,
  Pencil, Trash2, Check, X,
} from "lucide-react";

interface Pref { id: string; text: string }

export default function PreferencesPage() {
  const { id } = useParams<{ id: string }>();
  const [prefs, setPrefs] = useState<Pref[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<string | null>(null);
  const [editText, setEditText] = useState("");

  useEffect(() => {
    api.getPreferences(id)
      .then((res) => setPrefs(res.preferences))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  function startEdit(p: Pref) {
    setEditing(p.id);
    setEditText(p.text);
  }

  async function saveEdit(prefId: string) {
    try {
      await api.updatePreference(id, prefId, editText);
      setPrefs((prev) => prev.map((p) => p.id === prefId ? { ...p, text: editText } : p));
      setEditing(null);
    } catch (e) {
      console.error(e);
    }
  }

  async function removePref(prefId: string) {
    if (!confirm("Remove this preference?")) return;
    try {
      await api.removePreference(id, prefId);
      setPrefs((prev) => prev.filter((p) => p.id !== prefId));
    } catch (e) {
      console.error(e);
    }
  }

  return (
    <main className="max-w-5xl mx-auto px-6 pb-10">
      <div>
        <div className="flex items-center gap-3 mb-6">
          <BookOpen size={18} className="text-teal-DEFAULT" />
          <h2 className="text-base font-semibold text-slate-200">What I've Learned</h2>
        </div>

        {loading && <p className="text-slate-400 text-sm">Loading…</p>}

        {!loading && prefs.length === 0 && (
          <div className="surface p-10 text-center">
            <BookOpen size={32} className="text-slate-700 mx-auto mb-3" />
            <p className="text-slate-400 text-sm">No preferences learned yet.</p>
            <p className="text-slate-500 text-xs mt-1">Complete at least one calibration batch to see learned preferences here.</p>
          </div>
        )}

        {!loading && prefs.length > 0 && (
          <div className="space-y-3">
            {prefs.map((p) => (
              <div key={p.id} className="surface p-4 flex items-start gap-3">
                <div className="flex-1 min-w-0">
                  {editing === p.id ? (
                    <input
                      type="text"
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      onKeyDown={(e) => { if (e.key === "Enter") saveEdit(p.id); if (e.key === "Escape") setEditing(null); }}
                      autoFocus
                      className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-1.5 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-teal-DEFAULT"
                    />
                  ) : (
                    <p className="text-sm text-slate-200">{p.text}</p>
                  )}
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  {editing === p.id ? (
                    <>
                      <button onClick={() => saveEdit(p.id)} className="p-1.5 rounded hover:bg-slate-700 text-teal-light transition-colors">
                        <Check size={14} />
                      </button>
                      <button onClick={() => setEditing(null)} className="p-1.5 rounded hover:bg-slate-700 text-slate-400 transition-colors">
                        <X size={14} />
                      </button>
                    </>
                  ) : (
                    <>
                      <button onClick={() => startEdit(p)} className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition-colors">
                        <Pencil size={14} />
                      </button>
                      <button onClick={() => removePref(p.id)} className="p-1.5 rounded hover:bg-slate-700 text-slate-400 hover:text-rose-DEFAULT transition-colors">
                        <Trash2 size={14} />
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
