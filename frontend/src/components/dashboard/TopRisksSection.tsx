import React from "react";
import Link from "next/link";
import { AlertTriangle, ArrowRight, Shield } from "@/components/icons";
import { RiskCard } from "@/components/risks/RiskCard";
import { EmptyState } from "@/components/ui/EmptyState";
import { RiskEvent } from "@/types";

interface TopRisksSectionProps {
  risks: RiskEvent[];
  projectId: string;
}

export function TopRisksSection({ risks, projectId }: TopRisksSectionProps) {
  const activeRisks = risks.filter((r) => r.status === "new" || r.status === "active");
  const topRisks = activeRisks.slice(0, 4);

  return (
    <div className="space-y-3.5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-body-sm font-[510] tracking-[-0.011em] text-paper flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-acid-lime" />
            Top Emerging Delivery Risks
          </h3>
          <p className="text-caption text-fog mt-0.5">
            Priority risk alerts detected by telemetry and verified by AI investigation
          </p>
        </div>

        {activeRisks.length > 4 && (
          <Link
            href={`/projects/${projectId}/risks`}
            className="inline-flex items-center gap-1 text-caption font-[510] text-mist hover:text-paper transition-colors"
          >
            View all {activeRisks.length} risks
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        )}
      </div>

      {topRisks.length === 0 ? (
        <EmptyState
          icon={<Shield className="w-8 h-8 text-pulse-green" />}
          title="All Clear — Zero Active Risks"
          description="Your work items, dependencies, and milestones are on schedule with sustainable workload distribution."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          {topRisks.map((risk) => (
            <RiskCard key={risk.id} risk={risk} projectId={projectId} />
          ))}
        </div>
      )}
    </div>
  );
}
