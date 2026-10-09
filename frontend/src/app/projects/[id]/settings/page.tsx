"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { DataSourcesManager } from "@/components/settings/DataSourcesManager";
import { ThresholdsForm } from "@/components/settings/ThresholdsForm";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api } from "@/lib/api";
import { Project, ThresholdItem } from "@/types";

export default function ProjectSettingsPage() {
  const params = useParams();
  const projectId = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [thresholds, setThresholds] = useState<ThresholdItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSettings = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const [projData, threshData] = await Promise.all([
        api.getProject(projectId).catch(() => null),
        api.getThresholds(projectId).catch(() => ({ project_id: projectId, thresholds: [] })),
      ]);
      setProject(projData);
      setThresholds(threshData.thresholds || []);
    } catch (err) {
      console.error("Failed to load settings", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, [projectId]);

  return (
    <AppShell
      projectId={projectId}
      projectName={project?.name}
      health={project?.health}
      onRefresh={fetchSettings}
    >
      <PageHeader
        title="Project Settings & Sensitivity"
        subtitle="Manage risk threshold triggers, telemetry ingestion connectors, and monitoring parameters"
        breadcrumbs={[
          { label: "Dashboard", href: `/projects/${projectId}` },
          { label: "Settings" },
        ]}
      />

      {loading ? (
        <div className="space-y-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : (
        <div className="space-y-6">
          <ThresholdsForm
            projectId={projectId}
            initialThresholds={thresholds}
            onSave={fetchSettings}
          />

          <DataSourcesManager
            projectId={projectId}
            dataSources={project?.data_sources || []}
            onRefresh={fetchSettings}
          />
        </div>
      )}
    </AppShell>
  );
}
