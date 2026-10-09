import React from "react";
import Link from "next/link";
import { AlertTriangle, ArrowRight, Bot, ChevronRight, Clock, Shield } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { formatDate, getCategoryLabel, getSeverityBadge } from "@/lib/utils";
import { RiskEvent } from "@/types";

interface RiskCardProps {
  risk: RiskEvent;
  projectId: string;
}

export function RiskCard({ risk, projectId }: RiskCardProps) {
  const sevBadge = getSeverityBadge(risk.severity);
  const scorePercent = Math.round((risk.propensity_score || 0) * 100);

  // Extract primary evidence point if present
  const primaryEvidence = risk.signals?.[0]?.evidence?.[0]?.description || risk.description;
  const hasAgentInvestigation = !!risk.raw_metrics?.explanation;

  return (
    <Card
      hoverEffect
      glow={risk.severity === "critical" ? "rose" : risk.severity === "high" ? "amber" : "indigo"}
      className="p-5 flex flex-col justify-between"
    >
      <div>
        {/* Card Header: Category & Severity */}
        <div className="flex items-center justify-between gap-3 mb-2.5">
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider">
              {getCategoryLabel(risk.category)}
            </span>
            {hasAgentInvestigation && (
              <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
                <Bot className="w-3 h-3" />
                AI Analyzed
              </span>
            )}
          </div>

          <span
            className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border ${sevBadge.bg} ${sevBadge.text} ${sevBadge.border}`}
          >
            {risk.severity} ({scorePercent}%)
          </span>
        </div>

        {/* Risk Title */}
        <Link
          href={`/projects/${projectId}/risks/${risk.id}`}
          className="group block"
        >
          <h4 className="text-base font-semibold text-zinc-100 group-hover:text-indigo-400 transition-colors line-clamp-2">
            {risk.title}
          </h4>
        </Link>

        {/* Primary Evidence / Description */}
        <p className="text-xs text-zinc-400 mt-2 line-clamp-2 leading-relaxed">
          {primaryEvidence}
        </p>

        {/* Signal Tag or Metric */}
        {risk.signal_type && (
          <div className="mt-3 flex items-center gap-1.5 text-[11px] text-zinc-400 bg-zinc-950/60 px-2.5 py-1.5 rounded-lg border border-zinc-800/80">
            <AlertTriangle className="w-3.5 h-3.5 text-zinc-400 shrink-0" />
            <span className="font-mono text-zinc-300 truncate">{risk.signal_type}</span>
          </div>
        )}
      </div>

      {/* Footer / CTA */}
      <div className="mt-5 pt-3 border-t border-zinc-800/80 flex items-center justify-between">
        <span className="text-[11px] text-zinc-400">
          Detected: {formatDate(risk.created_at)}
        </span>

        <Link
          href={`/projects/${projectId}/risks/${risk.id}`}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
        >
          Investigate & Mitigate
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </Card>
  );
}
