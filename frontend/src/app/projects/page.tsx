"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Plus,
  RefreshCw,
  Shield,
} from "@/components/icons";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api } from "@/lib/api";
import { formatDate, getHealthBadge } from "@/lib/utils";
import { Project } from "@/types";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getProjects();
      setProjects(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to load projects";
      console.error("Failed to load projects", err);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <AppShell>
      <PageHeader
        title="Software Engineering Projects"
        subtitle="Monitored delivery pipelines and AI early-warning risk systems"
        actions={
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={fetchProjects} disabled={loading}>
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Link href="/projects/new">
              <Button variant="primary" size="md">
                <Plus className="w-3.5 h-3.5" />
                Connect New Project
              </Button>
            </Link>
          </div>
        }
      />

      {error && (
        <div className="mb-6 p-4 rounded-[6px] border border-[rgba(235,87,87,0.3)] bg-[rgba(235,87,87,0.1)] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-coral-red mt-1.5 flex-shrink-0" />
            <div>
              <h4 className="text-body-sm font-[510] text-coral-red">Backend Connection Error</h4>
              <p className="text-caption text-fog mt-0.5">{error}</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={fetchProjects} className="flex-shrink-0">
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Connection
          </Button>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : projects.length === 0 && !error ? (
        <div className="flex flex-col items-center justify-center p-16 text-center rounded-[12px] border border-graphite bg-carbon/50">
          <div className="w-10 h-10 rounded-[8px] bg-void border border-graphite flex items-center justify-center mb-4">
            <Shield className="w-5 h-5 text-acid-lime" />
          </div>
          <h3 className="text-body-sm font-[510] text-paper">No Monitored Projects</h3>
          <p className="text-caption text-fog max-w-sm mt-1 mb-6">
            Connect a GitHub repository or financial budget CSV to enable deterministic risk detection and AI mitigation workflows.
          </p>
          <Link href="/projects/new">
            <Button variant="primary" size="md">
              <Plus className="w-3.5 h-3.5" />
              Onboard First Project
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => {
            const healthBadge = getHealthBadge(project.health || "green");

            return (
              <Card
                key={project.id}
                hoverEffect
                className="p-5 flex flex-col justify-between border-graphite bg-carbon rounded-[12px] shadow-sm"
              >
                <div>
                  <div className="flex items-center justify-between gap-3 mb-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[4px] text-micro font-normal border ${healthBadge.bg} ${healthBadge.text} ${healthBadge.border}`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${healthBadge.dot} animate-pulse-dot`} />
                      {healthBadge.label}
                    </span>

                    <Badge variant="outline" size="sm">
                      {project.status.toUpperCase()}
                    </Badge>
                  </div>

                  <Link href={`/projects/${project.id}`} className="group block">
                    <h3 className="text-body-sm font-[510] text-paper group-hover:text-acid-lime transition-colors tracking-[-0.011em]">
                      {project.name}
                    </h3>
                  </Link>

                  <p className="text-caption text-fog mt-1.5 line-clamp-2 leading-relaxed">
                    {project.description || "Active software delivery pipeline."}
                  </p>

                  {/* Project metadata */}
                  <div className="mt-4 pt-3 border-t border-graphite flex items-center justify-between text-micro text-fog">
                    <span>Created: {formatDate(project.created_at)}</span>
                    <span className="font-mono text-mist">
                      DQ Reliability: {project.data_quality_score ? `${Math.round(project.data_quality_score)}%` : "95%"}
                    </span>
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-graphite flex items-center justify-between">
                  <span className="text-micro text-fog">
                    Type: <span className="text-mist capitalize">{project.project_type || "Software"}</span>
                  </span>

                  <Link
                    href={`/projects/${project.id}`}
                    className="inline-flex items-center gap-1 text-caption font-[510] text-mist hover:text-paper transition-colors"
                  >
                    Open Dashboard
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}
