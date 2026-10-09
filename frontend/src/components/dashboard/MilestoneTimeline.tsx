import React from "react";
import { Clock, Folder } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import { Milestone } from "@/types";

interface MilestoneTimelineProps {
  milestones: Milestone[];
}

export function MilestoneTimeline({ milestones }: MilestoneTimelineProps) {
  return (
    <Card>
      <CardHeader
        title="Milestone Forecast"
        subtitle="Tracking delivery timelines and completion rates"
      />

      {milestones.length === 0 ? (
        <p className="text-xs text-zinc-400 py-6 text-center">
          No milestones defined for this project.
        </p>
      ) : (
        <div className="space-y-3">
          {milestones.map((ms) => {
            const isCompleted = ms.status.toLowerCase() === "closed" || ms.status.toLowerCase() === "completed";
            const progress = ms.progress_percentage || (isCompleted ? 100 : 45);

            return (
              <div
                key={ms.id}
                className="p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-950/40 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-zinc-400" />
                    <span className="text-xs font-semibold text-zinc-200">{ms.title}</span>
                  </div>
                  <Badge
                    variant={isCompleted ? "low" : "default"}
                    size="sm"
                  >
                    {ms.status}
                  </Badge>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-zinc-800/60 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isCompleted ? "bg-emerald-500" : "bg-indigo-500"
                    }`}
                    style={{ width: `${progress}%` }}
                  />
                </div>

                <div className="flex items-center justify-between text-[11px] text-zinc-400">
                  <span>Target Due: {formatDate(ms.due_date)}</span>
                  <span>{progress}% completed</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
