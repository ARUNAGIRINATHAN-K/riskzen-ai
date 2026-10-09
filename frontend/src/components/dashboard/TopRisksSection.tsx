import React from "react";
import Link from "next/link";
import { AlertTriangle, ArrowRight, Shield } from "@/components/icons";
import { RiskCard } from "@/components/risks/RiskCard";
import { Button } from "@/components/ui/Button";
import { CardHeader } from "@/components/ui/Card";
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
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            Top Emerging Delivery Risks
          </h3>
          <p className="text-xs text-zinc-400 mt-0.5">
            Priority risk alerts detected by deterministic telemetry and verified by AI investigation
          </p>
        </div>

        {activeRisks.length > 4 && (
          <Link
            href={`/projects/${projectId}/risks`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            View all {activeRisks.length} risks
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        )}
      </div>

      {topRisks.length === 0 ? (
        <EmptyState
          icon={<Shield className="w-8 h-8 text-emerald-400" />}
          title="All Clear — Zero Active Risks"
          description="Your work items, dependencies, and milestones are on schedule with sustainable workload distribution."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {topRisks.map((risk) => (
            <RiskCard key={risk.id} risk={risk} projectId={projectId} />
          ))}
        </div>
      )}
    </div>
  );
}
