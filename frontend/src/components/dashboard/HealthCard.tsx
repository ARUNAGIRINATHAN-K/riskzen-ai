import React from "react";
import { Activity, AlertTriangle, CheckCircle, Shield } from "@/components/icons";
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
    <Card className="relative overflow-hidden bg-carbon border-graphite rounded-[12px] p-6 shadow-sm">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
        {/* Overall Status */}
        <div className="flex items-start gap-4">
          <div
            className={`w-12 h-12 rounded-[8px] flex items-center justify-center border shrink-0 ${badge.bg} ${badge.text} ${badge.border}`}
          >
            {health === "green" ? (
              <CheckCircle className="w-6 h-6" />
            ) : health === "yellow" || health === "orange" ? (
              <AlertTriangle className="w-6 h-6" />
            ) : (
              <Shield className="w-6 h-6" />
            )}
          </div>

          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-micro font-[510] uppercase tracking-wider text-fog">
                Project Delivery Health
              </span>
              <span
                className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-micro font-normal border ${badge.bg} ${badge.text} ${badge.border}`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${badge.dot} animate-pulse-dot`} />
                {badge.label}
              </span>
            </div>

            <h2 className="text-subheading font-[510] tracking-[-0.288px] text-paper">
              {health === "green"
                ? "On Track & Sustainable"
                : health === "yellow"
                ? "Early Warnings Detected"
                : health === "orange"
                ? "Delivery Threat Looming"
                : "Critical Intervention Required"}
            </h2>

            <p className="text-caption text-fog mt-1">
              {activeRisksCount === 0
                ? "No material delivery risks identified. Backlog and dependencies in healthy parameters."
                : `${activeRisksCount} active risk ${
                    activeRisksCount === 1 ? "signal requires" : "signals require"
                  } proactive mitigation.`}
            </p>
          </div>
        </div>

        {/* Metrics Pill Grid */}
        <div className="grid grid-cols-3 gap-2.5 shrink-0">
          <div className="px-4 py-2.5 rounded-[6px] bg-void border border-graphite text-center">
            <span className="text-micro text-fog block">Risk Score</span>
            <span className="text-body-lg font-mono font-[510] text-paper">{scorePercent}%</span>
          </div>

          <div className="px-4 py-2.5 rounded-[6px] bg-void border border-graphite text-center">
            <span className="text-micro text-fog block">AI Confidence</span>
            <span className="text-body-lg font-mono font-[510] text-acid-lime">{confidencePercent}%</span>
          </div>

          <div className="px-4 py-2.5 rounded-[6px] bg-void border border-graphite text-center">
            <span className="text-micro text-fog block">Data Quality</span>
            <span className="text-body-lg font-mono font-[510] text-pulse-green">
              {dataQualityScore !== undefined ? `${Math.round(dataQualityScore)}%` : "92%"}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
}
