"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { FileText, ArrowRight } from "lucide-react";

export default function NewJobPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !jd.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const job = await api.createJob({ title: title.trim(), jd_text: jd.trim() });
      router.push(`/jobs/${job.id}`);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="max-w-3xl mx-auto px-6 py-10">
      <div className="flex items-center gap-3 mb-8">
        <FileText className="text-teal-DEFAULT" size={22} />
        <h1 className="text-xl font-semibold">New Role</h1>
      </div>

      <form onSubmit={handleSubmit} className="surface p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Role title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Senior Python Backend Engineer"
            className="w-full bg-slate-800 border border-slate-700 rounded-md px-4 py-2.5 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-DEFAULT text-sm"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">Job description</label>
          <textarea
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste the full job description here…"
            rows={12}
            className="w-full bg-slate-800 border border-slate-700 rounded-md px-4 py-3 text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-teal-DEFAULT text-sm font-mono resize-none"
            required
          />
        </div>

        {error && <p className="text-rose-DEFAULT text-sm">{error}</p>}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center gap-2 px-5 py-2.5 rounded-md bg-teal-DEFAULT hover:bg-teal-dark disabled:opacity-50 text-white text-sm font-medium transition-colors"
          >
            {loading ? "Creating…" : "Create role"}
            <ArrowRight size={16} />
          </button>
        </div>
      </form>
    </main>
  );
}
