import React from "react";
import { Check, CheckCircle, Clock, Shield, Sliders, X } from "@/components/icons";
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
    <Card className="p-5 border-zinc-800 bg-zinc-900/80 space-y-4">
      {/* Card Header: Owner & Urgency */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Badge variant={urgencyBadge.variant} size="sm">
            {urgencyBadge.label}
          </Badge>
          <span className="text-xs text-zinc-400">
            Suggested Owner:{" "}
            <span className="font-semibold text-zinc-200">
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
        <h4 className="text-sm font-semibold text-zinc-100 leading-snug">
          {recommendation.action_description}
        </h4>
        <p className="text-xs text-zinc-400 mt-2 leading-relaxed">
          <span className="text-zinc-300 font-medium">Strategic Rationale:</span>{" "}
          {recommendation.rationale}
        </p>
      </div>

      {/* Decision rationale note if already decided */}
      {recommendation.decision_reason && (
        <div className="p-2.5 rounded-lg bg-zinc-950/60 border border-zinc-800 text-[11px] text-zinc-400">
          <span className="font-semibold text-zinc-300">Decision Note:</span>{" "}
          {recommendation.decision_reason}
        </div>
      )}

      {/* Decision Actions (PM Human-in-the-loop Controls) */}
      {isPending && (
        <div className="pt-3 border-t border-zinc-800 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDismiss(recommendation)}
              className="text-xs text-zinc-400 hover:text-rose-400"
            >
              <X className="w-3.5 h-3.5" />
              Dismiss
            </Button>

            <Button
              variant="outline"
              size="sm"
              onClick={() => onSnooze(recommendation)}
              className="text-xs text-zinc-400 hover:text-amber-400"
            >
              <Clock className="w-3.5 h-3.5" />
              Snooze
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => onModify(recommendation)}
              className="text-xs"
            >
              <Sliders className="w-3.5 h-3.5" />
              Modify
            </Button>
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={() => onApprove(recommendation)}
            className="text-xs"
          >
            <Check className="w-3.5 h-3.5" />
            Approve & Create Action
          </Button>
        </div>
      )}
    </Card>
  );
}
