"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type WorkspaceSettings } from "@/lib/api";
import { Settings, ArrowLeft, Check, X } from "lucide-react";

const ALL_ADAPTERS = ["mock", "github", "stackoverflow", "duckduckgo", "devto", "npm", "juicebox", "google_cse"];

function KeyBadge({ present }: { present: boolean }) {
  return present ? (
    <span className="flex items-center gap-1 text-xs text-teal-light"><Check size={11} /> Configured</span>
  ) : (
    <span className="flex items-center gap-1 text-xs text-slate-500"><X size={11} /> Not set</span>
  );
}

export default function SettingsPage() {
  const [data, setData] = useState<WorkspaceSettings | null>(null);
  const [apiKeys, setApiKeys] = useState<Record<string, boolean>>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [retentionDays, setRetentionDays] = useState(90);
  const [revealEnabled, setRevealEnabled] = useState(false);
  const [adapters, setAdapters] = useState<string[]>([]);

  useEffect(() => {
    api.getSettings().then((s) => {
      setData(s);
      setRetentionDays((s as any).retention_days ?? 90);
      setRevealEnabled((s as any).contact_reveal_enabled ?? false);
      setAdapters((s as any).source_adapters ?? []);
      setApiKeys((s as any).api_keys ?? {});
    }).catch(console.error);
  }, []);

  async function handleSave() {
    setSaving(true);
    setSaved(false);
    try {
      await api.updateSettings({
        retention_days: retentionDays,
        contact_reveal_enabled: revealEnabled,
        source_adapters: adapters,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error(e);
    } finally {
      setSaving(false);
    }
  }

  function toggleAdapter(name: string) {
    setAdapters((prev) =>
      prev.includes(name) ? prev.filter((a) => a !== name) : [...prev, name]
    );
  }

  return (
    <main className="max-w-2xl mx-auto px-6 py-10">
      <div className="flex items-center gap-3 mb-8">
        <Link href="/" className="p-1.5 rounded hover:bg-slate-800 text-slate-400 transition-colors">
          <ArrowLeft size={16} />
        </Link>
        <Settings size={18} className="text-teal-DEFAULT" />
        <h1 className="text-xl font-semibold text-slate-100">Workspace Settings</h1>
      </div>

      {!data ? (
        <p className="text-slate-400 text-sm">Loading…</p>
      ) : (
        <div className="space-y-6">
          {/* Retention */}
          <section className="surface p-5 space-y-3">
            <h2 className="text-sm font-semibold text-slate-200">Data Retention</h2>
            <div className="flex items-center gap-4">
              <label className="text-sm text-slate-400 w-48">Retention period (days)</label>
              <input
                type="number"
                min={1}
                max={3650}
                value={retentionDays}
                onChange={(e) => setRetentionDays(Number(e.target.value))}
                className="bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-sm text-slate-100 w-24 focus:outline-none focus:ring-2 focus:ring-teal-DEFAULT"
              />
            </div>
            <p className="text-xs text-slate-500">Candidate data is automatically deleted after this many days.</p>
          </section>

          {/* Contact reveal */}
          <section className="surface p-5 space-y-3">
            <h2 className="text-sm font-semibold text-slate-200">Contact Reveal</h2>
            <div className="flex items-center gap-4">
              <label className="text-sm text-slate-400 flex-1">Allow contact reveal by default</label>
              <button
                onClick={() => setRevealEnabled((v) => !v)}
                className={`relative w-10 h-5 rounded-full transition-colors ${revealEnabled ? "bg-teal-DEFAULT" : "bg-slate-700"}`}
              >
                <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${revealEnabled ? "translate-x-5" : ""}`} />
              </button>
            </div>
            <p className="text-xs text-slate-500">When enabled, recruiters can reveal contact info. Each reveal is logged.</p>
          </section>

          {/* Source adapters */}
          <section className="surface p-5 space-y-3">
            <h2 className="text-sm font-semibold text-slate-200">Active Source Adapters</h2>
            <div className="grid grid-cols-2 gap-2">
              {ALL_ADAPTERS.map((name) => (
                <label key={name} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={adapters.includes(name)}
                    onChange={() => toggleAdapter(name)}
                    className="accent-teal-DEFAULT"
                  />
                  <span className="text-sm text-slate-300 font-mono">{name}</span>
                </label>
              ))}
            </div>
          </section>

          {/* API keys (read-only) */}
          <section className="surface p-5 space-y-3">
            <h2 className="text-sm font-semibold text-slate-200">API Keys (set via environment)</h2>
            <div className="space-y-2">
              {[
                { label: "GitHub Token", key: "github_token" },
                { label: "Juicebox API Key", key: "juicebox_api_key" },
                { label: "Google CSE", key: "google_cse" },
                { label: "Stack Overflow Key", key: "stackoverflow_key" },
              ].map(({ label, key }) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">{label}</span>
                  <KeyBadge present={!!apiKeys[key]} />
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-500">Set these in your <code className="text-teal-light">.env</code> file. See <code className="text-teal-light">.env.example</code> for documentation.</p>
          </section>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-5 py-2 rounded bg-teal-DEFAULT hover:bg-teal-dark text-white text-sm font-medium transition-colors disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save Settings"}
            </button>
            {saved && <span className="text-xs text-teal-light flex items-center gap-1"><Check size={12} /> Saved</span>}
          </div>
        </div>
      )}
    </main>
  );
}
