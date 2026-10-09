import React from "react";
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2.5">
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
              className="p-3 rounded-[6px] border border-graphite bg-void hover:bg-carbon hover:border-smoke transition-all cursor-pointer group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-caption font-[510] text-mist group-hover:text-paper transition-colors truncate">
                  {getCategoryLabel(catKey)}
                </span>
                <span
                  className={`text-[10px] uppercase font-normal px-1.5 py-0.2 rounded-[4px] border ${badge.bg} ${badge.text} ${badge.border}`}
                >
                  {item.severity}
                </span>
              </div>

              {/* Progress score bar */}
              <div className="w-full bg-graphite/60 h-1 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    item.severity === "critical"
                      ? "bg-coral-red"
                      : item.severity === "high"
                      ? "bg-acid-lime"
                      : item.severity === "medium"
                      ? "bg-lavender"
                      : "bg-pulse-green"
                  }`}
                  style={{ width: `${Math.max(6, scorePercent)}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-micro text-fog font-mono">
                <span>{scorePercent}% propensity</span>
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
