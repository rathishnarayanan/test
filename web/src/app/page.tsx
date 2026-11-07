"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type Job } from "@/lib/api";
import { Briefcase, Plus, ChevronRight } from "lucide-react";

const STATUS_COLOR: Record<string, string> = {
  draft: "text-slate-400",
  sourcing: "text-amber-DEFAULT",
  calibrating: "text-teal-light",
  shortlisting: "text-teal-DEFAULT",
  outreach: "text-amber-DEFAULT",
  closed: "text-slate-500",
};

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listJobs().then(setJobs).catch(console.error).finally(() => setLoading(false));
  }, []);

  return (
    <main className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <Briefcase className="text-teal-DEFAULT" size={24} />
          <h1 className="text-xl font-semibold text-slate-100">Automatic Sourcing</h1>
        </div>
        <Link
          href="/jobs/new"
          className="flex items-center gap-2 px-4 py-2 rounded-md bg-teal-DEFAULT hover:bg-teal-dark text-white text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          New Role
        </Link>
      </div>

      {loading && <p className="text-slate-400 text-sm">Loading roles…</p>}

      {!loading && jobs.length === 0 && (
        <div className="surface p-10 text-center">
          <p className="text-slate-400 mb-4">No roles yet. Create your first one.</p>
          <Link href="/jobs/new" className="text-teal-light text-sm hover:underline">
            Create a role →
          </Link>
        </div>
      )}

      <div className="space-y-2">
        {jobs.map((job) => (
          <Link
            key={job.id}
            href={`/jobs/${job.id}`}
            className="surface flex items-center justify-between px-5 py-4 hover:border-slate-600 transition-colors group"
          >
            <div>
              <p className="font-medium text-slate-100 group-hover:text-teal-light transition-colors">{job.title}</p>
              <p className={`text-xs mt-0.5 font-mono ${STATUS_COLOR[job.status] ?? "text-slate-400"}`}>
                {job.status}
              </p>
            </div>
            <ChevronRight size={16} className="text-slate-500 group-hover:text-teal-light transition-colors" />
          </Link>
        ))}
      </div>
    </main>
  );
}
