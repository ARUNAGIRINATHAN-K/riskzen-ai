import React from "react";
import { ArrowRight, GitBranch } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { Dependency } from "@/types";

interface DependencySectionProps {
  dependencies: Dependency[];
}

export function DependencySection({ dependencies }: DependencySectionProps) {
  const blockingDeps = dependencies.filter((d) => d.dependency_type === "blocks" || !d.dependency_type);

  return (
    <Card>
      <CardHeader
        title="Dependency Bottlenecks"
        subtitle="Upstream blockers with potential cascade delay impact"
      />

      {blockingDeps.length === 0 ? (
        <p className="text-caption text-fog py-6 text-center">
          No blocking dependencies detected across active work items.
        </p>
      ) : (
        <div className="space-y-2">
          {blockingDeps.slice(0, 5).map((dep) => {
            const srcTitle = dep.source_item?.title || "Upstream Task";
            const tgtTitle = dep.target_item?.title || "Blocked Task";
            const isSrcDone =
              dep.source_item?.status.toLowerCase() === "closed" ||
              dep.source_item?.status.toLowerCase() === "done";

            return (
              <div
                key={dep.id}
                className="p-3 rounded-[6px] border border-graphite bg-void flex items-center justify-between gap-3"
              >
                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                  <div className="p-1.5 rounded-[4px] bg-carbon border border-graphite shrink-0">
                    <GitBranch className="w-3.5 h-3.5 text-fog" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-1.5 text-caption truncate">
                      <span className="font-[510] text-mist truncate">{srcTitle}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-ash shrink-0" />
                      <span className="font-[510] text-fog truncate">{tgtTitle}</span>
                    </div>

                    <span className="text-micro text-ash block mt-0.5">
                      Relationship: <span className="font-mono text-fog">BLOCKS</span>
                    </span>
                  </div>
                </div>

                <Badge variant={isSrcDone ? "low" : "critical"} size="sm">
                  {isSrcDone ? "Resolved" : "Active Blocker"}
                </Badge>
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
