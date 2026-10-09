"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  Folder,
  Plus,
  RefreshCw,
  Shield,
  Sparkles,
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
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={fetchProjects} disabled={loading}>
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
            <Link href="/projects/new">
              <Button variant="primary" size="md">
                <Plus className="w-4 h-4" />
                Connect New Project
              </Button>
            </Link>
          </div>
        }
      />

      {error && (
        <div className="mb-6 p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 rounded-full bg-rose-400 mt-2 flex-shrink-0" />
            <div>
              <h4 className="text-sm font-semibold text-rose-300">Backend Connection Error</h4>
              <p className="text-xs text-rose-200/80 mt-1">{error}</p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={fetchProjects} className="border-rose-500/40 text-rose-200 hover:bg-rose-500/20 flex-shrink-0">
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Connection
          </Button>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <CardSkeleton />
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : projects.length === 0 && !error ? (
        <div className="flex flex-col items-center justify-center p-16 text-center rounded-2xl border border-dashed border-zinc-800 bg-zinc-900/30">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-4">
            <Shield className="w-6 h-6 text-indigo-400" />
          </div>
          <h3 className="text-base font-semibold text-zinc-100">No Monitored Projects</h3>
          <p className="text-xs text-zinc-400 max-w-sm mt-1.5 mb-6">
            Connect a GitHub repository or financial budget CSV to enable deterministic risk detection and AI mitigation workflows.
          </p>
          <Link href="/projects/new">
            <Button variant="primary" size="md">
              <Plus className="w-4 h-4" />
              Onboard First Project
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => {
            const healthBadge = getHealthBadge(project.health || "green");

            return (
              <Card
                key={project.id}
                hoverEffect
                className="p-6 flex flex-col justify-between border-zinc-800 bg-zinc-900/70"
              >
                <div>
                  <div className="flex items-center justify-between gap-3 mb-3">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${healthBadge.bg} ${healthBadge.text} border-current/20`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${healthBadge.dot}`} />
                      {healthBadge.label}
                    </span>

                    <Badge variant="outline" size="sm">
                      {project.status.toUpperCase()}
                    </Badge>
                  </div>

                  <Link href={`/projects/${project.id}`} className="group block">
                    <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors">
                      {project.name}
                    </h3>
                  </Link>

                  <p className="text-xs text-zinc-400 mt-2 line-clamp-2 leading-relaxed">
                    {project.description || "Active software delivery pipeline."}
                  </p>

                  {/* Project metadata */}
                  <div className="mt-4 pt-4 border-t border-zinc-800/80 flex items-center justify-between text-[11px] text-zinc-400">
                    <span>Created: {formatDate(project.created_at)}</span>
                    <span className="font-medium text-zinc-300">
                      DQ Reliability: {project.data_quality_score ? `${Math.round(project.data_quality_score)}%` : "95%"}
                    </span>
                  </div>
                </div>

                <div className="mt-6 pt-3 border-t border-zinc-800 flex items-center justify-between">
                  <span className="text-xs text-zinc-400">
                    Type: <span className="text-zinc-200 capitalize">{project.project_type || "Software"}</span>
                  </span>

                  <Link
                    href={`/projects/${project.id}`}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors"
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
