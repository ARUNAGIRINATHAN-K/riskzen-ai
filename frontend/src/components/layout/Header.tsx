"use client";

import React, { useState } from "react";
import { RefreshCw, Sparkles } from "@/components/icons";
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
    <header className="h-14 border-b border-graphite bg-void px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <h2 className="text-body-sm font-[510] text-paper tracking-[-0.012em] truncate">
          {projectName || "RiskZen AI"}
        </h2>
        {projectId && (
          <span
            className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-label font-normal border ${healthBadge.bg} ${healthBadge.text} ${healthBadge.border}`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${healthBadge.dot} animate-pulse-dot`} />
            {healthBadge.label}
          </span>
        )}
      </div>

      {projectId && (
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleSync}
            isLoading={isSyncing}
          >
            <RefreshCw className="w-3.5 h-3.5 text-fog" />
            Sync Sources
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={handleEvaluate}
            isLoading={isEvaluating}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Run Risk Engine
          </Button>
        </div>
      )}
    </header>
  );
}
