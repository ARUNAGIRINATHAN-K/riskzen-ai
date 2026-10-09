"use client";

import React from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { ProjectHealth } from "@/types";

interface AppShellProps {
  projectId?: string;
  projectName?: string;
  health?: ProjectHealth;
  onRefresh?: () => void;
  children: React.ReactNode;
}

export function AppShell({
  projectId,
  projectName,
  health,
  onRefresh,
  children,
}: AppShellProps) {
  return (
    <div className="min-h-screen flex bg-zinc-950 text-zinc-100 font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
      <Sidebar projectId={projectId} projectName={projectName} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          projectId={projectId}
          projectName={projectName}
          health={health}
          onRefresh={onRefresh}
        />
        <main className="flex-1 p-8 max-w-7xl w-full mx-auto animate-in fade-in duration-200">
          {children}
        </main>
      </div>
    </div>
  );
}
