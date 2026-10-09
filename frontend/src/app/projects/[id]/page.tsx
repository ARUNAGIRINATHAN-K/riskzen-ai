"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { DependencySection } from "@/components/dashboard/DependencySection";
import { HealthCard } from "@/components/dashboard/HealthCard";
import { MilestoneTimeline } from "@/components/dashboard/MilestoneTimeline";
import { QuickStats } from "@/components/dashboard/QuickStats";
import { RiskCategoryDistribution } from "@/components/dashboard/RiskCategoryDistribution";
import { TopRisksSection } from "@/components/dashboard/TopRisksSection";
import { AppShell } from "@/components/layout/AppShell";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api } from "@/lib/api";
import {
  ActionListResponse,
  Dependency,
  Milestone,
  Project,
  RiskEvent,
  RiskSummaryResponse,
} from "@/types";

export default function ProjectDashboardPage() {
  const params = useParams();
  const projectId = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [summary, setSummary] = useState<RiskSummaryResponse | null>(null);
  const [risks, setRisks] = useState<RiskEvent[]>([]);
  const [actions, setActions] = useState<ActionListResponse | null>(null);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [dependencies, setDependencies] = useState<Dependency[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const [projData, summaryData, risksData, actionsData, milestonesData, depsData] =
        await Promise.all([
          api.getProject(projectId).catch(() => null),
          api.getRiskSummary(projectId).catch(() => null),
          api.getRisks(projectId).catch(() => []),
          api.getActions(projectId).catch(() => null),
          api.getMilestones(projectId).catch(() => []),
          api.getDependencies(projectId).catch(() => []),
        ]);

      setProject(projData);
      setSummary(summaryData);
      setRisks(risksData);
      setActions(actionsData);
      setMilestones(milestonesData);
      setDependencies(depsData);
    } catch (err) {
      console.error("Failed to load dashboard telemetry", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [projectId]);

  const criticalRisks = risks.filter((r) => r.severity === "critical" && r.status !== "resolved");
  const highRisks = risks.filter((r) => r.severity === "high" && r.status !== "resolved");

  return (
    <AppShell
      projectId={projectId}
      projectName={project?.name}
      health={project?.health}
      onRefresh={fetchDashboardData}
    >
      {loading ? (
        <div className="space-y-6">
          <CardSkeleton />
          <div className="grid grid-cols-4 gap-4">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
          <CardSkeleton />
        </div>
      ) : (
        <div className="space-y-8">
          {/* Top Health Card */}
          <HealthCard
            health={project?.health || "green"}
            riskScore={summary?.overall_score || 0.0}
            confidence={summary?.confidence || 0.85}
            activeRisksCount={summary?.total_active_risks || 0}
            lastEvaluatedAt={summary?.last_evaluated_at}
            dataQualityScore={project?.data_quality_score}
          />

          {/* Quick Metrics */}
          <QuickStats
            criticalCount={criticalRisks.length}
            highCount={highRisks.length}
            openActionsCount={actions?.open_actions || 0}
            overdueActionsCount={actions?.overdue_actions || 0}
            upcomingMilestonesCount={milestones.length}
          />

          {/* Top Prioritized Risks */}
          <TopRisksSection risks={risks} projectId={projectId} />

          {/* 7 Risk Categories Taxonomy Grid */}
          <RiskCategoryDistribution categories={summary?.category_summaries || {}} />

          {/* Milestones & Dependencies Split */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MilestoneTimeline milestones={milestones} />
            <DependencySection dependencies={dependencies} />
          </div>
        </div>
      )}
    </AppShell>
  );
}
