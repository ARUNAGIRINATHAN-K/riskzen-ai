import React from "react";
import { Activity, AlertTriangle, CheckCircle, Shield } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { getHealthBadge } from "@/lib/utils";
import { ProjectHealth } from "@/types";

interface HealthCardProps {
  health: ProjectHealth;
  riskScore: number;
  confidence: number;
  activeRisksCount: number;
  lastEvaluatedAt?: string;
  dataQualityScore?: number;
}

export function HealthCard({
  health,
  riskScore,
  confidence,
  activeRisksCount,
  lastEvaluatedAt,
  dataQualityScore,
}: HealthCardProps) {
  const badge = getHealthBadge(health);
  const scorePercent = Math.round(riskScore * 100);
  const confidencePercent = Math.round(confidence * 100);

  return (
    <Card className="relative overflow-hidden bg-gradient-to-br from-zinc-900/90 via-zinc-900/70 to-zinc-950 border-zinc-800">
      {/* Background ambient glow based on health */}
      <div
        className={`absolute -top-12 -right-12 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none ${
          health === "red"
            ? "bg-rose-500"
            : health === "orange"
            ? "bg-amber-500"
            : health === "yellow"
            ? "bg-yellow-500"
            : "bg-emerald-500"
        }`}
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        {/* Overall Status */}
        <div className="flex items-start gap-4">
          <div
            className={`w-14 h-14 rounded-2xl flex items-center justify-center border shrink-0 ${badge.bg} ${badge.text} border-current/30 shadow-lg shadow-black/40`}
          >
            {health === "green" ? (
              <CheckCircle className="w-7 h-7" />
            ) : health === "yellow" || health === "orange" ? (
              <AlertTriangle className="w-7 h-7" />
            ) : (
              <Shield className="w-7 h-7" />
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Project Delivery Health
              </span>
              <span
                className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold ${badge.bg} ${badge.text}`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
                {badge.label}
              </span>
            </div>

            <h2 className="text-2xl font-bold tracking-tight text-white">
              {health === "green"
                ? "On Track & Sustainable"
                : health === "yellow"
                ? "Early Warnings Detected"
                : health === "orange"
                ? "Delivery Threat Looming"
                : "Critical Intervention Required"}
            </h2>

            <p className="text-xs text-zinc-400 mt-1">
              {activeRisksCount === 0
                ? "No material delivery risks identified. Backlog and dependencies in healthy parameters."
                : `${activeRisksCount} active risk ${
                    activeRisksCount === 1 ? "signal requires" : "signals require"
                  } proactive mitigation.`}
            </p>
          </div>
        </div>

        {/* Metrics Pill Grid */}
        <div className="grid grid-cols-3 gap-3 shrink-0">
          <div className="px-4 py-2.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80 text-center">
            <span className="text-[11px] text-zinc-400 block">Risk Propensity</span>
            <span className="text-lg font-bold text-zinc-100">{scorePercent}%</span>
          </div>

          <div className="px-4 py-2.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80 text-center">
            <span className="text-[11px] text-zinc-400 block">AI Confidence</span>
            <span className="text-lg font-bold text-indigo-400">{confidencePercent}%</span>
          </div>

          <div className="px-4 py-2.5 rounded-xl bg-zinc-950/60 border border-zinc-800/80 text-center">
            <span className="text-[11px] text-zinc-400 block">Data Quality</span>
            <span className="text-lg font-bold text-emerald-400">
              {dataQualityScore !== undefined ? `${Math.round(dataQualityScore)}%` : "92%"}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
