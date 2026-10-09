"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { CheckCircle } from "@/components/icons";
import { ActionItemRow } from "@/components/actions/ActionItemRow";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
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

      <div className="space-y-4">
        {/* Status Metrics Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
          <Card className="p-4 bg-carbon border-graphite rounded-[12px]">
            <span className="text-caption text-fog">Total Actions</span>
            <span className="text-subheading font-mono font-[510] text-paper block mt-1">
              {actionsData?.total_actions || 0}
            </span>
          </Card>

          <Card className="p-4 bg-carbon border-graphite rounded-[12px]">
            <span className="text-caption text-acid-lime">Open In-Flight</span>
            <span className="text-subheading font-mono font-[510] text-acid-lime block mt-1">
              {actionsData?.open_actions || 0}
            </span>
          </Card>

          <Card className="p-4 bg-carbon border-graphite rounded-[12px]">
            <span className="text-caption text-pulse-green">Completed</span>
            <span className="text-subheading font-mono font-[510] text-pulse-green block mt-1">
              {actionsData?.completed_actions || 0}
            </span>
          </Card>

          <Card className="p-4 bg-carbon border-graphite rounded-[12px]">
            <span className="text-caption text-coral-red">Overdue SLA Target</span>
            <span className="text-subheading font-mono font-[510] text-coral-red block mt-1">
              {actionsData?.overdue_actions || 0}
            </span>
          </Card>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 border-b border-graphite pb-3">
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
              className={`px-3 py-1 rounded-[6px] text-caption font-[510] transition-colors ${
                statusFilter === tab.id
                  ? "bg-carbon text-paper border border-graphite shadow-sm"
                  : "text-fog hover:text-mist hover:bg-[rgba(255,255,255,0.03)]"
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
            icon={<CheckCircle className="w-8 h-8 text-pulse-green" />}
            title="No Mitigation Actions"
            description="Approved recommendations from AI agent investigations will appear here for execution tracking."
          />
        ) : (
          <div className="space-y-2.5">
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
