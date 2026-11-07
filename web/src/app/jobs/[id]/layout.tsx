"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api, type Job } from "@/lib/api";
import { Briefcase } from "lucide-react";
import { JobNav } from "@/components/JobNav";

export default function JobLayout({ children }: { children: React.ReactNode }) {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);

  useEffect(() => {
    api.getJob(id).then(setJob).catch(() => {});
  }, [id]);

  return (
    <>
      <div className="max-w-7xl mx-auto px-6 py-10 pb-0">
        <div className="flex items-center gap-2 mb-6">
          <Briefcase size={18} className="text-teal-DEFAULT" />
          <h1 className="text-xl font-semibold">{job?.title ?? id}</h1>
        </div>
        <JobNav id={id} />
      </div>
      {children}
    </>
  );
}
