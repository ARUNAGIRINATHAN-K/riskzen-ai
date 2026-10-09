"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Shield, Sparkles } from "@/components/icons";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { RiskCard } from "@/components/risks/RiskCard";
import { RiskFilters } from "@/components/risks/RiskFilters";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api } from "@/lib/api";
import { Project, RiskEvent } from "@/types";

export default function RisksListPage() {
  const params = useParams();
  const projectId = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [risks, setRisks] = useState<RiskEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [isEvaluating, setIsEvaluating] = useState(false);

  // Filter States
  const [category, setCategory] = useState("");
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [search, setSearch] = useState("");

  const fetchRisks = async () => {
    if (!projectId) return;
    try {
      setLoading(true);
      const [projData, risksData] = await Promise.all([
        api.getProject(projectId).catch(() => null),
        api.getRisks(projectId, {
          category: category || undefined,
          severity: severity || undefined,
          status: status || undefined,
        }).catch(() => []),
      ]);
      setProject(projData);
      setRisks(risksData);
    } catch (err) {
      console.error("Failed to load risks", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRisks();
  }, [projectId, category, severity, status]);

  const handleEvaluate = async () => {
    try {
      setIsEvaluating(true);
      await api.evaluateRisks(projectId);
      await fetchRisks();
    } catch (err) {
      console.error("Evaluation failed", err);
    } finally {
      setIsEvaluating(false);
    }
  };

  const filteredRisks = risks.filter((r) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      r.title.toLowerCase().includes(q) ||
      r.description.toLowerCase().includes(q) ||
      (r.signal_type || "").toLowerCase().includes(q)
    );
  });

  return (
    <AppShell
      projectId={projectId}
      projectName={project?.name}
      health={project?.health}
      onRefresh={fetchRisks}
    >
      <PageHeader
        title="Delivery Risk Radar"
        subtitle="Real-time deterministic telemetry and prioritized early-warning alerts"
        breadcrumbs={[
          { label: "Dashboard", href: `/projects/${projectId}` },
          { label: "Risks" },
        ]}
        actions={
          <Button
            variant="primary"
            size="md"
            onClick={handleEvaluate}
            isLoading={isEvaluating}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Evaluate Risks Now
          </Button>
        }
      />

      <div className="space-y-4">
        {/* Filters Bar */}
        <RiskFilters
          category={category}
          setCategory={setCategory}
          severity={severity}
          setSeverity={setSeverity}
          status={status}
          setStatus={setStatus}
          search={search}
          setSearch={setSearch}
        />

        {/* Risks Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
            <CardSkeleton />
          </div>
        ) : filteredRisks.length === 0 ? (
          <EmptyState
            icon={<Shield className="w-8 h-8 text-pulse-green" />}
            title="No Risks Matching Active Filters"
            description="All active work items and milestones within the selected filter criteria are healthy."
            action={
              (category || severity || status || search) && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setCategory("");
                    setSeverity("");
                    setStatus("");
                    setSearch("");
                  }}
                >
                  Clear Filters
                </Button>
              )
            }
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            {filteredRisks.map((risk) => (
              <RiskCard key={risk.id} risk={risk} projectId={projectId} />
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
