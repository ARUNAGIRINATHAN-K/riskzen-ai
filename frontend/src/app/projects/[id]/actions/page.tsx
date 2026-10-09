"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { CheckCircle, Clock, Layers } from "@/components/icons";
import { ActionItemRow } from "@/components/actions/ActionItemRow";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api } from "@/lib/api";
import { ActionListResponse, Project } from "@/types";

export default function ActionsTrackingPage() {
  const params = useParams();
  const projectId = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [actionsData, setActionsData] = useState<ActionListResponse | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const fetchActions = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const [projData, actData] = await Promise.all([
        api.getProject(projectId).catch(() => null),
        api.getActions(projectId, statusFilter || undefined).catch(() => null),
      ]);
      setProject(projData);
      setActionsData(actData);
    } catch (err) {
      console.error("Failed to load actions", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
  }, [projectId, statusFilter]);

  const handleCompleteAction = async (actionId: string) => {
    try {
      await api.completeAction(actionId);
      await fetchActions();
    } catch (err) {
      console.error("Failed to complete action", err);
    }
  };

  return (
    <AppShell
      projectId={projectId}
      projectName={project?.name}
      health={project?.health}
      onRefresh={fetchActions}
    >
      <PageHeader
        title="Mitigation Actions Board"
        subtitle="Track approved risk mitigation tasks and team accountability"
        breadcrumbs={[
          { label: "Dashboard", href: `/projects/${projectId}` },
          { label: "Actions" },
        ]}
      />

      <div className="space-y-6">
        {/* Status Metrics Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <Card className="p-4 bg-zinc-900/60 border-zinc-800">
            <span className="text-xs text-zinc-400">Total Tracked Actions</span>
            <span className="text-2xl font-bold text-white block mt-1">
              {actionsData?.total_actions || 0}
            </span>
          </Card>

          <Card className="p-4 bg-zinc-900/60 border-zinc-800">
            <span className="text-xs text-indigo-400">Open In-Flight</span>
            <span className="text-2xl font-bold text-indigo-300 block mt-1">
              {actionsData?.open_actions || 0}
            </span>
          </Card>

          <Card className="p-4 bg-zinc-900/60 border-zinc-800">
            <span className="text-xs text-emerald-400">Successfully Completed</span>
            <span className="text-2xl font-bold text-emerald-300 block mt-1">
              {actionsData?.completed_actions || 0}
            </span>
          </Card>

          <Card className="p-4 bg-zinc-900/60 border-zinc-800">
            <span className="text-xs text-rose-400">Overdue SLA Target</span>
            <span className="text-2xl font-bold text-rose-300 block mt-1">
              {actionsData?.overdue_actions || 0}
            </span>
          </Card>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2 border-b border-zinc-800 pb-3">
          {[
            { id: "", label: "All Actions" },
            { id: "pending", label: "Pending" },
            { id: "in_progress", label: "In Progress" },
            { id: "overdue", label: "Overdue" },
            { id: "completed", label: "Completed" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setStatusFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                statusFilter === tab.id
                  ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Action Items List */}
        {loading ? (
          <div className="space-y-3">
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : !actionsData?.actions || actionsData.actions.length === 0 ? (
          <EmptyState
            icon={<CheckCircle className="w-10 h-10 text-emerald-400" />}
            title="No Mitigation Actions"
            description="Approved recommendations from AI agent investigations will appear here for execution tracking."
          />
        ) : (
          <div className="space-y-3">
            {actionsData.actions.map((action) => (
              <ActionItemRow
                key={action.id}
                action={action}
                onComplete={handleCompleteAction}
              />
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
