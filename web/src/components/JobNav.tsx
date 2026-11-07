"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Settings, Users, BarChart2, Zap, MessageSquare, GitBranch, BookOpen, FileText } from "lucide-react";

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

export function JobNav({ id }: { id: string }) {
  const pathname = usePathname();
  return (
    <div className="flex gap-1 mb-8 overflow-x-auto pb-1">
      {NAV.map(({ label, icon: Icon, href }) => {
        const active = pathname === `/jobs/${id}${href}`;
        return (
          <Link
            key={label}
            href={`/jobs/${id}${href}`}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition-colors whitespace-nowrap ${
              active
                ? "bg-slate-800 text-teal-light"
                : "text-slate-300 hover:text-teal-light hover:bg-slate-800"
            }`}
          >
            <Icon size={14} />
            {label}
          </Link>
        );
      })}
    </div>
  );
}
