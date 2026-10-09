"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Activity, AlertTriangle, CheckCircle, Shield, TrendingUp } from "@/components/icons";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api } from "@/lib/api";
import { formatDateTime, getCategoryLabel } from "@/lib/utils";
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
        <div className="space-y-6">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : (
        <div className="space-y-8">
          {/* Top Summary Banner */}
          <Card className="p-6 bg-gradient-to-r from-indigo-950/40 via-zinc-900 to-zinc-900 border-zinc-800">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div>
                <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block mb-1">
                  Executive Briefing
                </span>
                <h3 className="text-xl font-bold text-white">
                  {project?.name} — Delivery Trajectory
                </h3>
                <p className="text-xs text-zinc-400 mt-1 max-w-xl">
                  Deterministic telemetry identified {activeRisks.length} active delivery risks and resolved {resolvedRisks.length} threats across all 7 monitored taxonomy categories.
                </p>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                <div className="text-center px-4 py-2 rounded-xl bg-zinc-950 border border-zinc-800">
                  <span className="text-[11px] text-zinc-400 block">Active Risks</span>
                  <span className="text-xl font-bold text-amber-400">{activeRisks.length}</span>
                </div>
                <div className="text-center px-4 py-2 rounded-xl bg-zinc-950 border border-zinc-800">
                  <span className="text-[11px] text-zinc-400 block">Resolved</span>
                  <span className="text-xl font-bold text-emerald-400">{resolvedRisks.length}</span>
                </div>
                <div className="text-center px-4 py-2 rounded-xl bg-zinc-950 border border-zinc-800">
                  <span className="text-[11px] text-zinc-400 block">Actions Done</span>
                  <span className="text-xl font-bold text-indigo-400">{actions?.completed_actions || 0}</span>
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
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-zinc-800 text-zinc-400">
                    <th className="pb-3 font-semibold">Category</th>
                    <th className="pb-3 font-semibold">Severity Level</th>
                    <th className="pb-3 font-semibold">Score</th>
                    <th className="pb-3 font-semibold">Signals Detected</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/60">
                  {Object.entries(summary?.category_summaries || {}).map(([catKey, cat]) => (
                    <tr key={catKey} className="hover:bg-zinc-900/40">
                      <td className="py-3 font-medium text-zinc-200">{getCategoryLabel(catKey)}</td>
                      <td className="py-3">
                        <Badge variant={cat.severity} size="sm">
                          {cat.severity.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="py-3 font-mono font-bold text-zinc-100">
                        {Math.round(cat.score * 100)}%
                      </td>
                      <td className="py-3 text-zinc-400">{cat.signal_count} items</td>
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
