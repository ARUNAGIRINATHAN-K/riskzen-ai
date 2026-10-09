import React from "react";
import { Check, Clock, Sliders, X } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Recommendation } from "@/types";

interface RecommendationCardProps {
  recommendation: Recommendation;
  onApprove: (rec: Recommendation) => void;
  onModify: (rec: Recommendation) => void;
  onDismiss: (rec: Recommendation) => void;
  onSnooze: (rec: Recommendation) => void;
}

export function RecommendationCard({
  recommendation,
  onApprove,
  onModify,
  onDismiss,
  onSnooze,
}: RecommendationCardProps) {
  const isPending = recommendation.status === "pending";

  const urgencyBadge = {
    immediate: { variant: "critical" as const, label: "Immediate (Today)" },
    today: { variant: "high" as const, label: "High Urgency" },
    this_week: { variant: "medium" as const, label: "This Week" },
    optional: { variant: "low" as const, label: "Discretionary" },
  }[recommendation.urgency] || { variant: "medium" as const, label: "This Week" };

  return (
    <Card className="p-5 border-graphite bg-carbon rounded-[12px] space-y-4">
      {/* Card Header: Owner & Urgency */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Badge variant={urgencyBadge.variant} size="sm">
            {urgencyBadge.label}
          </Badge>
          <span className="text-caption text-fog">
            Suggested Owner:{" "}
            <span className="font-[510] text-mist">
              {recommendation.suggested_owner || "Project Lead"}
            </span>
          </span>
        </div>

        {/* Status indicator */}
        <Badge
          variant={
            recommendation.status === "approved"
              ? "low"
              : recommendation.status === "modified"
              ? "info"
              : recommendation.status === "dismissed"
              ? "critical"
              : recommendation.status === "snoozed"
              ? "medium"
              : "outline"
          }
          size="sm"
        >
          {recommendation.status.toUpperCase()}
        </Badge>
      </div>

      {/* Action Description */}
      <div>
        <h4 className="text-body-sm font-[510] text-paper leading-snug tracking-[-0.011em]">
          {recommendation.action_description}
        </h4>
        <p className="text-caption text-fog mt-1.5 leading-relaxed">
          <span className="text-mist font-[510]">Strategic Rationale:</span>{" "}
          {recommendation.rationale}
        </p>
      </div>

      {/* Decision rationale note if already decided */}
      {recommendation.decision_reason && (
        <div className="p-2.5 rounded-[6px] bg-void border border-graphite text-caption text-fog">
          <span className="font-[510] text-mist">Decision Note:</span>{" "}
          {recommendation.decision_reason}
        </div>
      )}

      {/* Decision Actions (PM Human-in-the-loop Controls) */}
      {isPending && (
        <div className="pt-3 border-t border-graphite flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDismiss(recommendation)}
            >
              <X className="w-3.5 h-3.5 text-coral-red" />
              Dismiss
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => onSnooze(recommendation)}
            >
              <Clock className="w-3.5 h-3.5 text-lavender" />
              Snooze
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => onModify(recommendation)}
            >
              <Sliders className="w-3.5 h-3.5 text-mist" />
              Modify
            </Button>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={() => onApprove(recommendation)}
          >
            <Check className="w-3.5 h-3.5" />
            Approve & Create Action
          </Button>
        </div>
      )}
    </Card>
  );
}
