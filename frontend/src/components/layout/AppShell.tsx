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
    <div className="min-h-screen flex bg-void text-mist font-sans">
      <Sidebar projectId={projectId} projectName={projectName} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          projectId={projectId}
          projectName={projectName}
          health={health}
          onRefresh={onRefresh}
        />
        <main className="flex-1 p-6 md:p-8 max-w-[1200px] w-full mx-auto animate-fade-in">
          {children}
        </main>
      </div>
    </div>
  );
}
