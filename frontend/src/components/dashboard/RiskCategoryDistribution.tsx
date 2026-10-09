import React from "react";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { getCategoryLabel, getSeverityBadge } from "@/lib/utils";
import { RiskCategorySummary } from "@/types";

interface RiskCategoryDistributionProps {
  categories: Record<string, RiskCategorySummary>;
  onCategoryClick?: (category: string) => void;
}

export function RiskCategoryDistribution({
  categories,
  onCategoryClick,
}: RiskCategoryDistributionProps) {
  const categoryOrder = [
    "schedule",
    "dependency",
    "capacity",
    "scope",
    "quality",
    "budget",
    "decision",
  ];

  return (
    <Card>
      <CardHeader
        title="Risk Taxonomy Distribution"
        subtitle="Evaluated propensity score across all 7 deterministic risk categories"
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
        {categoryOrder.map((catKey) => {
          const item = categories[catKey] || {
            category: catKey,
            score: 0.0,
            severity: "low",
            signal_count: 0,
          };
          const badge = getSeverityBadge(item.severity);
          const scorePercent = Math.round(item.score * 100);

          return (
            <div
              key={catKey}
              onClick={() => onCategoryClick && onCategoryClick(catKey)}
              className="p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-950/40 hover:bg-zinc-900/60 hover:border-zinc-700 transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-zinc-300 group-hover:text-white transition-colors truncate">
                  {getCategoryLabel(catKey)}
                </span>
                <span
                  className={`text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full border ${badge.bg} ${badge.text} ${badge.border}`}
                >
                  {item.severity}
                </span>
              </div>

              {/* Progress score bar */}
              <div className="w-full bg-zinc-800/60 h-1.5 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    item.severity === "critical"
                      ? "bg-rose-500"
                      : item.severity === "high"
                      ? "bg-amber-500"
                      : item.severity === "medium"
                      ? "bg-yellow-500"
                      : "bg-emerald-500"
                  }`}
                  style={{ width: `${Math.max(6, scorePercent)}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[11px] text-zinc-400">
                <span>{scorePercent}% risk score</span>
                <span>
                  {item.signal_count} {item.signal_count === 1 ? "signal" : "signals"}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
