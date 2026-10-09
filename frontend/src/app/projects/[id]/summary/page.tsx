"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api } from "@/lib/api";
import { getCategoryLabel } from "@/lib/utils";
import { ActionListResponse, Project, RiskEvent, RiskSummaryResponse } from "@/types";

export default function WeeklySummaryPage() {
  const params = useParams();
  const projectId = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [summary, setSummary] = useState<RiskSummaryResponse | null>(null);
  const [risks, setRisks] = useState<RiskEvent[]>([]);
  const [actions, setActions] = useState<ActionListResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchSummary = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const [projData, summaryData, risksData, actionsData] = await Promise.all([
        api.getProject(projectId).catch(() => null),
        api.getRiskSummary(projectId).catch(() => null),
        api.getRisks(projectId).catch(() => []),
        api.getActions(projectId).catch(() => null),
      ]);
      setProject(projData);
      setSummary(summaryData);
      setRisks(risksData);
      setActions(actionsData);
    } catch (err) {
      console.error("Failed to load summary", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, [projectId]);

  const activeRisks = risks.filter((r) => r.status === "new" || r.status === "active");
  const resolvedRisks = risks.filter((r) => r.status === "resolved" || r.status === "closed");

  return (
    <AppShell
      projectId={projectId}
      projectName={project?.name}
      health={project?.health}
      onRefresh={fetchSummary}
    >
      <PageHeader
        title="Weekly Risk & Governance Summary"
        subtitle="Aggregated risk trajectory, resolved threats, and mitigation velocity"
        breadcrumbs={[
          { label: "Dashboard", href: `/projects/${projectId}` },
          { label: "Weekly Summary" },
        ]}
      />

      {loading ? (
        <div className="space-y-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Top Summary Banner */}
          <Card className="p-6 bg-carbon border-graphite rounded-[12px] shadow-sm">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <span className="text-micro font-[510] text-mist uppercase tracking-wider block mb-1">
                  Executive Briefing
                </span>
                <h3 className="text-subheading font-[510] text-paper tracking-[-0.288px]">
                  {project?.name} — Delivery Trajectory
                </h3>
                <p className="text-caption text-fog mt-1 max-w-xl">
                  Deterministic telemetry identified {activeRisks.length} active delivery risks and resolved {resolvedRisks.length} threats across all 7 monitored taxonomy categories.
                </p>
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <div className="text-center px-4 py-2 rounded-[6px] bg-void border border-graphite">
                  <span className="text-micro text-fog block">Active Risks</span>
                  <span className="text-body-lg font-mono font-[510] text-acid-lime">{activeRisks.length}</span>
                </div>
                <div className="text-center px-4 py-2 rounded-[6px] bg-void border border-graphite">
                  <span className="text-micro text-fog block">Resolved</span>
                  <span className="text-body-lg font-mono font-[510] text-pulse-green">{resolvedRisks.length}</span>
                </div>
                <div className="text-center px-4 py-2 rounded-[6px] bg-void border border-graphite">
                  <span className="text-micro text-fog block">Actions Done</span>
                  <span className="text-body-lg font-mono font-[510] text-mist">{actions?.completed_actions || 0}</span>
                </div>
              </div>
            </div>
          </Card>

          {/* Category Breakdown Table */}
          <Card>
            <CardHeader
              title="Taxonomy Category Risk Health"
              subtitle="Current propensity index by category"
            />

            <div className="overflow-x-auto">
              <table className="w-full text-left text-caption">
                <thead>
                  <tr className="border-b border-graphite text-fog">
                    <th className="pb-2.5 font-[510]">Category</th>
                    <th className="pb-2.5 font-[510]">Severity Level</th>
                    <th className="pb-2.5 font-[510]">Score</th>
                    <th className="pb-2.5 font-[510]">Signals Detected</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-graphite/60">
                  {Object.entries(summary?.category_summaries || {}).map(([catKey, cat]) => (
                    <tr key={catKey} className="hover:bg-[rgba(255,255,255,0.02)]">
                      <td className="py-2.5 font-[510] text-mist">{getCategoryLabel(catKey)}</td>
                      <td className="py-2.5">
                        <Badge variant={cat.severity} size="sm">
                          {cat.severity.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="py-2.5 font-mono font-[510] text-paper">
                        {Math.round(cat.score * 100)}%
                      </td>
                      <td className="py-2.5 text-fog">{cat.signal_count} items</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
