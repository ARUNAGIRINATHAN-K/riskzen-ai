import React from "react";
import { AlertTriangle, ArrowRight, GitBranch } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { Dependency } from "@/types";

interface DependencySectionProps {
  dependencies: Dependency[];
}

export function DependencySection({ dependencies }: DependencySectionProps) {
  // Filter for blockers
  const blockingDeps = dependencies.filter((d) => d.dependency_type === "blocks" || !d.dependency_type);

  return (
    <Card>
      <CardHeader
        title="Dependency Bottlenecks"
        subtitle="Upstream blockers with potential cascade delay impact"
      />

      {blockingDeps.length === 0 ? (
        <p className="text-xs text-zinc-400 py-6 text-center">
          No blocking dependencies detected across active work items.
        </p>
      ) : (
        <div className="space-y-3">
          {blockingDeps.slice(0, 5).map((dep) => {
            const srcTitle = dep.source_item?.title || "Upstream Task";
            const tgtTitle = dep.target_item?.title || "Blocked Task";
            const isSrcDone =
              dep.source_item?.status.toLowerCase() === "closed" ||
              dep.source_item?.status.toLowerCase() === "done";

            return (
              <div
                key={dep.id}
                className="p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-950/40 flex items-center justify-between gap-3"
              >
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <div className="p-2 rounded-lg bg-zinc-800/60 shrink-0">
                    <GitBranch className="w-4 h-4 text-indigo-400" />
                  </div>

                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 text-xs truncate">
                      <span className="font-medium text-zinc-200 truncate">{srcTitle}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                      <span className="font-medium text-zinc-400 truncate">{tgtTitle}</span>
                    </div>

                    <span className="text-[11px] text-zinc-400 block mt-0.5">
                      Relationship: <span className="font-mono text-zinc-300">BLOCKS</span>
                    </span>
                  </div>
                </div>

                <Badge variant={isSrcDone ? "low" : "high"} size="sm">
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
