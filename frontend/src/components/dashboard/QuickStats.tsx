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
      icon: <AlertTriangle className="w-5 h-5 text-rose-400" />,
      highlight: criticalCount > 0 ? "border-rose-500/30" : "border-zinc-800",
    },
    {
      label: "Pending Mitigation Actions",
      value: openActionsCount,
      sublabel: `${overdueActionsCount} Overdue SLA`,
      icon: <Layers className="w-5 h-5 text-indigo-400" />,
      highlight: overdueActionsCount > 0 ? "border-amber-500/30" : "border-zinc-800",
    },
    {
      label: "Active Milestones",
      value: upcomingMilestonesCount,
      sublabel: "Target deliveries tracked",
      icon: <Clock className="w-5 h-5 text-emerald-400" />,
      highlight: "border-zinc-800",
    },
    {
      label: "Agent Governance",
      value: "Human-in-Loop",
      sublabel: "Zero auto-actions without PM",
      icon: <Shield className="w-5 h-5 text-purple-400" />,
      highlight: "border-zinc-800",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, i) => (
        <Card key={i} className={`p-4 ${stat.highlight} bg-zinc-900/60`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-zinc-400">{stat.label}</span>
            <div className="p-2 rounded-lg bg-zinc-800/60 border border-zinc-700/40">
              {stat.icon}
            </div>
          </div>
          <div className="mt-2">
            <span className="text-2xl font-bold text-white tracking-tight">{stat.value}</span>
            <span className="text-[11px] text-zinc-400 block mt-0.5">{stat.sublabel}</span>
          </div>
        </Card>
      ))}
    </div>
  );
}
