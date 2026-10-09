"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  FileText,
  Folder,
  Layers,
  Shield,
  Sliders,
  TrendingUp,
} from "@/components/icons";
import { cn } from "@/lib/utils";

interface SidebarProps {
  projectId?: string;
  projectName?: string;
}

export function Sidebar({ projectId, projectName }: SidebarProps) {
  const pathname = usePathname();

  const navItems = projectId
    ? [
        {
          label: "Dashboard",
          href: `/projects/${projectId}`,
          icon: <Activity className="w-4 h-4" />,
          exact: true,
        },
        {
          label: "Risks & Radar",
          href: `/projects/${projectId}/risks`,
          icon: <AlertTriangle className="w-4 h-4" />,
        },
        {
          label: "Mitigation Actions",
          href: `/projects/${projectId}/actions`,
          icon: <Layers className="w-4 h-4" />,
        },
        {
          label: "Weekly Summary",
          href: `/projects/${projectId}/summary`,
          icon: <TrendingUp className="w-4 h-4" />,
        },
        {
          label: "Audit Trail",
          href: `/projects/${projectId}/audit`,
          icon: <FileText className="w-4 h-4" />,
        },
        {
          label: "Settings & Sensitivity",
          href: `/projects/${projectId}/settings`,
          icon: <Sliders className="w-4 h-4" />,
        },
      ]
    : [
        {
          label: "All Projects",
          href: "/projects",
          icon: <Folder className="w-4 h-4" />,
          exact: true,
        },
      ];

  return (
    <aside className="w-64 shrink-0 flex flex-col border-r border-graphite bg-void h-screen sticky top-0 z-40 select-none">
      {/* Brand Header */}
      <div className="h-14 px-5 flex items-center justify-between border-b border-graphite">
        <Link href="/projects" className="flex items-center gap-2.5 group">
          <div className="w-6 h-6 rounded-[6px] bg-carbon border border-graphite flex items-center justify-center text-paper group-hover:border-smoke transition-colors">
            <Shield className="w-3.5 h-3.5 text-paper" />
          </div>
          <span className="text-body-sm font-[510] tracking-[-0.012em] text-paper flex items-center gap-1.5">
            RiskZen
            <span className="text-micro font-[510] px-1 py-0.2 bg-[rgba(228,242,34,0.12)] text-acid-lime border border-[rgba(228,242,34,0.25)] rounded-[4px]">
              AI
            </span>
          </span>
        </Link>
      </div>

      {/* Active Project Card / Switcher */}
      {projectId && (
        <div className="px-3 py-2.5 border-b border-graphite bg-carbon/50">
          <Link
            href="/projects"
            className="flex items-center justify-between group p-2 rounded-[6px] hover:bg-carbon border border-transparent hover:border-graphite transition-all"
          >
            <div className="truncate">
              <span className="text-micro font-[510] text-fog uppercase tracking-wider block">
                Active Project
              </span>
              <span className="text-caption font-[510] text-mist group-hover:text-paper transition-colors truncate block">
                {projectName || "Project Dashboard"}
              </span>
            </div>
            <span className="text-micro font-normal text-fog group-hover:text-mist bg-graphite/60 px-1.5 py-0.5 rounded-[4px]">
              Switch
            </span>
          </Link>
        </div>
      )}

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-3 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = item.exact
            ? pathname === item.href
            : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 px-2.5 py-1.5 rounded-[6px] text-caption transition-colors duration-150 tracking-[-0.011em]",
                isActive
                  ? "bg-carbon text-paper font-[510] border border-graphite shadow-sm"
                  : "text-fog hover:text-mist hover:bg-[rgba(255,255,255,0.03)]"
              )}
            >
              <span className={cn(isActive ? "text-paper" : "text-ash")}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer System Status */}
      <div className="p-3.5 border-t border-graphite text-micro text-ash flex items-center justify-between">
        <span className="font-mono">LangGraph Engine</span>
        <div className="flex items-center gap-1.5 text-fog">
          <span className="w-1.5 h-1.5 rounded-full bg-pulse-green animate-pulse-dot" />
          <span>Active</span>
        </div>
      </div>
    </aside>
  );
}
