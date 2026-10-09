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
  Settings,
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
    <aside className="w-64 shrink-0 flex flex-col border-r border-zinc-800 bg-zinc-950/80 backdrop-blur-xl h-screen sticky top-0 z-40">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-zinc-800/80">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-purple-600 flex items-center justify-center shadow-md shadow-indigo-600/30">
          <Shield className="w-4 h-4 text-white" />
        </div>
        <div>
          <span className="text-base font-bold tracking-tight text-white flex items-center gap-1.5">
            RiskZen <span className="text-[10px] uppercase font-semibold px-1.5 py-0.2 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded">AI</span>
          </span>
          <span className="text-[11px] text-zinc-500 block -mt-0.5">Early Warning System</span>
        </div>
      </div>

      {/* Project Context Switcher */}
      {projectId && (
        <div className="px-4 py-3 border-b border-zinc-800/60 bg-zinc-900/40">
          <Link
            href="/projects"
            className="flex items-center justify-between group p-2 rounded-lg hover:bg-zinc-800/50 transition-colors"
          >
            <div className="truncate">
              <span className="text-[10px] uppercase tracking-wider text-zinc-500 block font-semibold">Active Project</span>
              <span className="text-xs font-medium text-zinc-200 group-hover:text-indigo-400 transition-colors truncate block">
                {projectName || "Project Dashboard"}
              </span>
            </div>
            <span className="text-[10px] text-zinc-400 group-hover:text-zinc-200 bg-zinc-800 px-1.5 py-0.5 rounded">
              Switch
            </span>
          </Link>
        </div>
      )}

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = item.exact
            ? pathname === item.href
            : pathname.startsWith(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-150",
                isActive
                  ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/30 font-semibold shadow-sm"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/60"
              )}
            >
              <span className={cn(isActive ? "text-indigo-400" : "text-zinc-500")}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer System Info */}
      <div className="p-4 border-t border-zinc-800/80 text-[11px] text-zinc-500 flex items-center justify-between">
        <span>Deterministic + LangGraph</span>
        <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" title="System Online" />
      </div>
    </aside>
  );
}
