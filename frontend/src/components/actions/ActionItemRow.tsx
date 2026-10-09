import React from "react";
import { Check, CheckCircle, Clock, Layers, User } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import { Action } from "@/types";

interface ActionItemRowProps {
  action: Action;
  onComplete: (actionId: string) => void;
}

export function ActionItemRow({ action, onComplete }: ActionItemRowProps) {
  const isCompleted = action.status === "completed";
  const isOverdue = action.status === "overdue";

  const statusBadge = {
    completed: { variant: "low" as const, label: "Completed" },
    in_progress: { variant: "info" as const, label: "In Progress" },
    overdue: { variant: "critical" as const, label: "Overdue" },
    pending: { variant: "medium" as const, label: "Pending" },
  }[action.status] || { variant: "default" as const, label: action.status };

  return (
    <Card className="p-4 border-graphite bg-carbon rounded-[12px] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex items-start gap-3 min-w-0 flex-1">
        <div
          className={`p-2 rounded-[6px] shrink-0 mt-0.5 border ${
            isCompleted
              ? "bg-[rgba(39,166,68,0.10)] text-pulse-green border-[rgba(39,166,68,0.25)]"
              : isOverdue
              ? "bg-[rgba(235,87,87,0.10)] text-coral-red border-[rgba(235,87,87,0.25)]"
              : "bg-void text-acid-lime border-graphite"
          }`}
        >
          {isCompleted ? <CheckCircle className="w-4 h-4" /> : <Layers className="w-4 h-4" />}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h4
              className={`text-body-sm font-[510] tracking-[-0.011em] ${
                isCompleted ? "line-through text-fog" : "text-paper"
              }`}
            >
              {action.description}
            </h4>
            <Badge variant={statusBadge.variant} size="sm">
              {statusBadge.label}
            </Badge>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-caption text-fog mt-1">
            <span className="flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-ash" />
              Owner: <span className="text-mist font-[510]">{action.owner}</span>
            </span>

            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-ash" />
              Target Due:{" "}
              <span className={`font-mono ${isOverdue ? "text-coral-red font-bold" : "text-mist"}`}>
                {formatDate(action.due_date)}
              </span>
            </span>
          </div>
        </div>
      </div>

      {!isCompleted && (
        <Button
          variant="outline"
          size="sm"
          onClick={() => onComplete(action.id)}
          className="shrink-0 self-end sm:self-center"
        >
          <Check className="w-3.5 h-3.5 text-pulse-green" />
          Mark Completed
        </Button>
      )}
    </Card>
  );
}
