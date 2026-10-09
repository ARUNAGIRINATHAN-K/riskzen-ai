import React from "react";
import { Clock } from "@/components/icons";
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
        <p className="text-caption text-fog py-6 text-center">
          No milestones defined for this project.
        </p>
      ) : (
        <div className="space-y-2">
          {milestones.map((ms) => {
            const isCompleted = ms.status.toLowerCase() === "closed" || ms.status.toLowerCase() === "completed";
            const progress = ms.progress_percentage || (isCompleted ? 100 : 45);

            return (
              <div
                key={ms.id}
                className="p-3 rounded-[6px] border border-graphite bg-void space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Clock className="w-3.5 h-3.5 text-fog" />
                    <span className="text-caption font-[510] text-mist">{ms.title}</span>
                  </div>
                  <Badge
                    variant={isCompleted ? "low" : "default"}
                    size="sm"
                  >
                    {ms.status}
                  </Badge>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-graphite/60 h-1 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isCompleted ? "bg-pulse-green" : "bg-acid-lime"
                    }`}
                    style={{ width: `${progress}%` }}
                  />
                </div>

                <div className="flex items-center justify-between text-micro text-fog font-mono">
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
