"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AuditTimeline } from "@/components/audit/AuditTimeline";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api, fetchApi } from "@/lib/api";
import { AuditLog, Project } from "@/types";

export default function AuditTrailPage() {
  const params = useParams();
  const projectId = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAuditLogs = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const [projData, auditData] = await Promise.all([
        api.getProject(projectId).catch(() => null),
        fetchApi<AuditLog[]>(`/projects/${projectId}/audit`).catch(() => []),
      ]);
      setProject(projData);
      setLogs(auditData);
    } catch (err) {
      console.error("Failed to load audit logs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, [projectId]);

  return (
    <AppShell
      projectId={projectId}
      projectName={project?.name}
      health={project?.health}
      onRefresh={fetchAuditLogs}
    >
      <PageHeader
        title="Immutable Audit & Governance Ledger"
        subtitle="Complete chronological history of AI detections, PM approvals, modifications, and outcomes"
        breadcrumbs={[
          { label: "Dashboard", href: `/projects/${projectId}` },
          { label: "Audit Trail" },
        ]}
      />

      {loading ? (
        <CardSkeleton />
      ) : (
        <AuditTimeline logs={logs} />
      )}
    </AppShell>
  );
}
