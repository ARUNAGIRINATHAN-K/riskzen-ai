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
    <Card className="p-4 border-zinc-800 bg-zinc-900/60 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div className="flex items-start gap-3 min-w-0 flex-1">
        <div
          className={`p-2 rounded-xl shrink-0 mt-0.5 ${
            isCompleted
              ? "bg-emerald-500/10 text-emerald-400"
              : isOverdue
              ? "bg-rose-500/10 text-rose-400"
              : "bg-indigo-500/10 text-indigo-400"
          }`}
        >
          {isCompleted ? <CheckCircle className="w-5 h-5" /> : <Layers className="w-5 h-5" />}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <h4
              className={`text-sm font-semibold tracking-tight ${
                isCompleted ? "line-through text-zinc-400" : "text-zinc-100"
              }`}
            >
              {action.description}
            </h4>
            <Badge variant={statusBadge.variant} size="sm">
              {statusBadge.label}
            </Badge>
          </div>

          <div className="flex flex-wrap items-center gap-4 text-xs text-zinc-400 mt-1">
            <span className="flex items-center gap-1.5">
              <User className="w-3.5 h-3.5 text-zinc-400" />
              Owner: <span className="text-zinc-300 font-medium">{action.owner}</span>
            </span>

            <span className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-zinc-400" />
              Target Due:{" "}
              <span className={`font-medium ${isOverdue ? "text-rose-400 font-bold" : "text-zinc-300"}`}>
                {formatDate(action.due_date)}
              </span>
            </span>
          </div>
        </div>
      </div>

      {!isCompleted && (
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onComplete(action.id)}
          className="text-xs shrink-0 self-end sm:self-center"
        >
          <Check className="w-3.5 h-3.5 text-emerald-400" />
          Mark Completed
        </Button>
      )}
    </Card>
  );
}
