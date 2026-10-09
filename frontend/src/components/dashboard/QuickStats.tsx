import React from "react";
import { AlertTriangle, Clock, Layers, Shield } from "@/components/icons";
import { Card } from "@/components/ui/Card";

interface QuickStatsProps {
  criticalCount: number;
  highCount: number;
  openActionsCount: number;
  overdueActionsCount: number;
  upcomingMilestonesCount: number;
}

export function QuickStats({
  criticalCount,
  highCount,
  openActionsCount,
  overdueActionsCount,
  upcomingMilestonesCount,
}: QuickStatsProps) {
  const stats = [
    {
      label: "Critical & High Risks",
      value: criticalCount + highCount,
      sublabel: `${criticalCount} Critical, ${highCount} High`,
      icon: <AlertTriangle className="w-4 h-4 text-coral-red" />,
      border: criticalCount > 0 ? "border-[rgba(235,87,87,0.3)]" : "border-graphite",
    },
    {
      label: "Pending Actions",
      value: openActionsCount,
      sublabel: `${overdueActionsCount} Overdue SLA`,
      icon: <Layers className="w-4 h-4 text-acid-lime" />,
      border: overdueActionsCount > 0 ? "border-[rgba(228,242,34,0.3)]" : "border-graphite",
    },
    {
      label: "Active Milestones",
      value: upcomingMilestonesCount,
      sublabel: "Target deliveries tracked",
      icon: <Clock className="w-4 h-4 text-pulse-green" />,
      border: "border-graphite",
    },
    {
      label: "Agent Governance",
      value: "Human-in-Loop",
      sublabel: "Zero auto-actions without PM",
      icon: <Shield className="w-4 h-4 text-iris-violet" />,
      border: "border-graphite",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      {stats.map((stat, i) => (
        <Card key={i} className={`p-4 border ${stat.border} bg-carbon rounded-[12px]`}>
          <div className="flex items-center justify-between">
            <span className="text-caption font-normal text-fog">{stat.label}</span>
            <div className="p-1.5 rounded-[6px] bg-void border border-graphite">
              {stat.icon}
            </div>
          </div>
          <div className="mt-2">
            <span className="text-subheading font-mono font-[510] text-paper tracking-[-0.288px]">
              {stat.value}
            </span>
            <span className="text-micro text-ash block mt-0.5">{stat.sublabel}</span>
          </div>
        </Card>
      ))}
    </div>
  );
}
