import React from "react";
import Link from "next/link";
import { AlertTriangle, Bot, ChevronRight } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
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

  const primaryEvidence = risk.signals?.[0]?.evidence?.[0]?.description || risk.description;
  const hasAgentInvestigation = !!risk.raw_metrics?.explanation;

  return (
    <Card
      hoverEffect
      className="p-5 flex flex-col justify-between bg-carbon border-graphite rounded-[12px] shadow-sm"
    >
      <div>
        {/* Card Header: Category & Severity */}
        <div className="flex items-center justify-between gap-3 mb-2.5">
          <div className="flex items-center gap-2">
            <span className="text-micro font-[510] text-mist uppercase tracking-wider">
              {getCategoryLabel(risk.category)}
            </span>
            {hasAgentInvestigation && (
              <span className="inline-flex items-center gap-1 text-micro px-1.5 py-0.2 rounded-[4px] bg-[rgba(99,102,241,0.10)] text-iris-violet border border-[rgba(99,102,241,0.20)]">
                <Bot className="w-3 h-3" />
                AI Verified
              </span>
            )}
          </div>

          <span
            className={`text-micro uppercase font-normal px-1.5 py-0.2 rounded-[4px] border ${sevBadge.bg} ${sevBadge.text} ${sevBadge.border}`}
          >
            {risk.severity} ({scorePercent}%)
          </span>
        </div>

        {/* Risk Title */}
        <Link
          href={`/projects/${projectId}/risks/${risk.id}`}
          className="group block"
        >
          <h4 className="text-body-sm font-[510] text-paper group-hover:text-acid-lime transition-colors line-clamp-2 tracking-[-0.011em]">
            {risk.title}
          </h4>
        </Link>

        {/* Primary Evidence / Description */}
        <p className="text-caption text-fog mt-1.5 line-clamp-2 leading-relaxed">
          {primaryEvidence}
        </p>

        {/* Signal Tag or Metric */}
        {risk.signal_type && (
          <div className="mt-3 flex items-center gap-1.5 text-micro text-fog bg-void px-2.5 py-1.5 rounded-[6px] border border-graphite">
            <AlertTriangle className="w-3.5 h-3.5 text-ash shrink-0" />
            <span className="font-mono text-mist truncate">{risk.signal_type}</span>
          </div>
        )}
      </div>

      {/* Footer / CTA */}
      <div className="mt-4 pt-3 border-t border-graphite flex items-center justify-between">
        <span className="text-micro text-ash">
          Detected: {formatDate(risk.created_at)}
        </span>

        <Link
          href={`/projects/${projectId}/risks/${risk.id}`}
          className="inline-flex items-center gap-1 text-caption font-[510] text-mist hover:text-paper transition-colors"
        >
          Investigate
          <ChevronRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </Card>
  );
}
