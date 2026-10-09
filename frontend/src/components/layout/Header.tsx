"use client";

import React, { useState } from "react";
import { Activity, RefreshCw, Sparkles } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { getHealthBadge } from "@/lib/utils";
import { ProjectHealth } from "@/types";

interface HeaderProps {
  projectId?: string;
  projectName?: string;
  health?: ProjectHealth;
  onRefresh?: () => void;
}

export function Header({ projectId, projectName, health = "green", onRefresh }: HeaderProps) {
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const healthBadge = getHealthBadge(health);

  const handleEvaluate = async () => {
    if (!projectId) return;
    try {
      setIsEvaluating(true);
      await api.evaluateRisks(projectId);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error("Risk evaluation failed", err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleSync = async () => {
    if (!projectId) return;
    try {
      setIsSyncing(true);
      await api.triggerSync(projectId);
      if (onRefresh) onRefresh();
    } catch (err) {
      console.error("Sync failed", err);
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <header className="h-16 border-b border-zinc-800 bg-zinc-950/40 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-medium text-zinc-200 truncate">
          {projectName || "RiskZen AI"}
        </h2>
        {projectId && (
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${healthBadge.bg} ${healthBadge.text} border-current/20`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${healthBadge.dot} animate-pulse`} />
            {healthBadge.label}
          </span>
        )}
      </div>

      {projectId && (
        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={handleSync}
            isLoading={isSyncing}
            className="text-xs"
          >
            <RefreshCw className="w-3.5 h-3.5 text-zinc-400" />
            Sync Sources
          </Button>

          <Button
            variant="gradient"
            size="sm"
            onClick={handleEvaluate}
            isLoading={isEvaluating}
            className="text-xs"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Run Risk Engine
          </Button>
        </div>
      )}
    </header>
  );
}
