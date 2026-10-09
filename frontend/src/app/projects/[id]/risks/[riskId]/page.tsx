"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Shield,
  Sparkles,
} from "@/components/icons";
import { AppShell } from "@/components/layout/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import {
  ApproveModal,
  DismissModal,
  ModifyModal,
  OutcomeModal,
  SnoozeModal,
} from "@/components/recommendations/DecisionModals";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { RiskEvidenceViewer } from "@/components/risks/RiskEvidenceViewer";
import { RootCauseSection } from "@/components/risks/RootCauseSection";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { api } from "@/lib/api";
import { formatDate, getCategoryLabel, getSeverityBadge } from "@/lib/utils";
import { Project, Recommendation, RiskEvent } from "@/types";

export default function RiskDetailPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params?.id as string;
  const riskId = params?.riskId as string;

  const [project, setProject] = useState<Project | null>(null);
  const [risk, setRisk] = useState<RiskEvent | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [isInvestigating, setIsInvestigating] = useState(false);

  // Modal states
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null);
  const [modalType, setModalType] = useState<"approve" | "modify" | "dismiss" | "snooze" | "outcome" | null>(null);

  const fetchRiskData = async () => {
    if (!projectId || !riskId) return;
    try {
      setLoading(true);
      const [projData, riskData, recsData] = await Promise.all([
        api.getProject(projectId).catch(() => null),
        api.getRiskDetail(projectId, riskId).catch(() => null),
        api.getRecommendations(riskId).catch(() => []),
      ]);
      setProject(projData);
      setRisk(riskData);
      setRecommendations(recsData);
    } catch (err) {
      console.error("Failed to load risk details", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRiskData();
  }, [projectId, riskId]);

  const handleInvestigate = async () => {
    try {
      setIsInvestigating(true);
      await api.triggerInvestigation(riskId);
      await fetchRiskData();
    } catch (err) {
      console.error("Investigation failed", err);
    } finally {
      setIsInvestigating(false);
    }
  };

  // Modal Handlers
  const handleApproveConfirm = async (recId: string, owner?: string, dueDate?: string) => {
    await api.approveRecommendation(recId, { owner, due_date: dueDate });
    await fetchRiskData();
  };

  const handleModifyConfirm = async (
    recId: string,
    actionDesc: string,
    owner: string,
    dueDate?: string,
    reason?: string
  ) => {
    await api.modifyRecommendation(recId, {
      action_description: actionDesc,
      owner,
      due_date: dueDate,
      reason,
    });
    await fetchRiskData();
  };

  const handleDismissConfirm = async (recId: string, reason: string) => {
    await api.dismissRecommendation(recId, reason);
    await fetchRiskData();
  };

  const handleSnoozeConfirm = async (recId: string, hours: number, reason?: string) => {
    await api.snoozeRecommendation(recId, hours, reason);
    await fetchRiskData();
  };

  const handleOutcomeConfirm = async (
    rId: string,
    result: "yes" | "partially" | "no" | "not_sure",
    comment?: string
  ) => {
    await api.recordOutcome(rId, { result, feedback_comment: comment });
    await fetchRiskData();
  };

  const sevBadge = risk ? getSeverityBadge(risk.severity) : null;

  return (
    <AppShell
      projectId={projectId}
      projectName={project?.name}
      health={project?.health}
      onRefresh={fetchRiskData}
    >
      <PageHeader
        title={risk?.title || "Risk Event Detail"}
        subtitle={`Detected in ${risk ? getCategoryLabel(risk.category) : "Category"}`}
        breadcrumbs={[
          { label: "Dashboard", href: `/projects/${projectId}` },
          { label: "Risks", href: `/projects/${projectId}/risks` },
          { label: "Investigation & Mitigation" },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="md"
              onClick={() => setModalType("outcome")}
            >
              <Shield className="w-3.5 h-3.5 text-mist" />
              Record Outcome
            </Button>

            <Button
              variant="primary"
              size="md"
              onClick={handleInvestigate}
              isLoading={isInvestigating}
            >
              <Sparkles className="w-3.5 h-3.5" />
              Run Agent Investigation
            </Button>
          </div>
        }
      />

      {loading || !risk ? (
        <div className="space-y-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Risk Overview Header Card */}
          <Card className="p-5 border-graphite bg-carbon rounded-[12px] shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`text-micro uppercase font-normal px-2 py-0.5 rounded-[4px] border ${sevBadge?.bg} ${sevBadge?.text} ${sevBadge?.border}`}
                >
                  {risk.severity} Severity ({Math.round(risk.propensity_score * 100)}%)
                </span>

                <Badge variant="purple" size="md">
                  Category: {getCategoryLabel(risk.category)}
                </Badge>

                <Badge variant="outline" size="md">
                  Status: {risk.status.toUpperCase()}
                </Badge>
              </div>

              <div className="flex items-center gap-4 text-micro text-fog font-mono">
                <span>Detected: {formatDate(risk.created_at)}</span>
                <span>Signal: <code className="text-mist">{risk.signal_type}</code></span>
              </div>
            </div>

            <p className="text-body-sm text-paper mt-3.5 leading-relaxed font-normal">
              {risk.description}
            </p>
          </Card>

          {/* AI Agent Root Cause Analysis Section */}
          <RootCauseSection
            risk={risk}
            onReinvestigate={handleInvestigate}
            isInvestigating={isInvestigating}
          />

          {/* Mitigation Recommendations Section */}
          <div className="space-y-3.5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-body-sm font-[510] text-paper tracking-[-0.011em]">
                  Proposed Mitigation Actions ({recommendations.length})
                </h3>
                <p className="text-caption text-fog mt-0.5">
                  Actionable mitigation interventions requiring PM approval before execution
                </p>
              </div>
            </div>

            {recommendations.length === 0 ? (
              <Card className="p-8 text-center text-fog text-caption bg-carbon border-graphite rounded-[12px]">
                No recommendations generated yet. Click &quot;Run Agent Investigation&quot; above to synthesize mitigation options.
              </Card>
            ) : (
              <div className="space-y-2.5">
                {recommendations.map((rec) => (
                  <RecommendationCard
                    key={rec.id}
                    recommendation={rec}
                    onApprove={(r) => {
                      setSelectedRec(r);
                      setModalType("approve");
                    }}
                    onModify={(r) => {
                      setSelectedRec(r);
                      setModalType("modify");
                    }}
                    onDismiss={(r) => {
                      setSelectedRec(r);
                      setModalType("dismiss");
                    }}
                    onSnooze={(r) => {
                      setSelectedRec(r);
                      setModalType("snooze");
                    }}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Supporting Evidence Trail */}
          <RiskEvidenceViewer signals={risk.signals} />
        </div>
      )}

      {/* Decision Modals */}
      <ApproveModal
        isOpen={modalType === "approve"}
        onClose={() => setModalType(null)}
        recommendation={selectedRec}
        onConfirm={handleApproveConfirm}
      />

      <ModifyModal
        isOpen={modalType === "modify"}
        onClose={() => setModalType(null)}
        recommendation={selectedRec}
        onConfirm={handleModifyConfirm}
      />

      <DismissModal
        isOpen={modalType === "dismiss"}
        onClose={() => setModalType(null)}
        recommendation={selectedRec}
        onConfirm={handleDismissConfirm}
      />

      <SnoozeModal
        isOpen={modalType === "snooze"}
        onClose={() => setModalType(null)}
        recommendation={selectedRec}
        onConfirm={handleSnoozeConfirm}
      />

      <OutcomeModal
        isOpen={modalType === "outcome"}
        onClose={() => setModalType(null)}
        riskId={riskId}
        onConfirm={handleOutcomeConfirm}
      />
    </AppShell>
  );
}
