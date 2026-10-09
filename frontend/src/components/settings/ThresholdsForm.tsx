"use client";

import React, { useState } from "react";
import { Check, RefreshCw, Sliders } from "@/components/icons";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { ThresholdItem } from "@/types";

interface ThresholdsFormProps {
  projectId: string;
  initialThresholds: ThresholdItem[];
  onSave?: () => void;
}

export function ThresholdsForm({ projectId, initialThresholds, onSave }: ThresholdsFormProps) {
  const [values, setValues] = useState<Record<string, number>>(() => {
    const map: Record<string, number> = {};
    initialThresholds.forEach((t) => {
      map[t.name] = t.value;
    });
    return map;
  });

  const [isSaving, setIsSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState(false);

  const handleChange = (name: string, val: number) => {
    setValues((prev) => ({ ...prev, [name]: val }));
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      await api.updateThresholds(projectId, values);
      setSavedMessage(true);
      setTimeout(() => setSavedMessage(false), 3000);
      if (onSave) onSave();
    } catch (err) {
      console.error("Failed to save thresholds", err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRestoreDefaults = () => {
    const defaults: Record<string, number> = {
      overdue_task_days: 1.0,
      milestone_slippage_days: 1.0,
      aging_task_days: 7.0,
      dependency_blocker_days: 2.0,
      scope_growth_rate: 0.2,
      requirement_churn_rate: 0.25,
      capacity_concentration_ratio: 0.4,
      max_wip_per_member: 5.0,
      defect_ratio_threshold: 0.3,
      critical_bug_sla_days: 7.0,
      budget_variance_threshold: 0.2,
      blocker_staleness_days: 5.0,
      pr_review_sla_days: 4.0,
    };
    setValues(defaults);
  };

  return (
    <Card>
      <CardHeader
        title="Risk Detection Sensitivity & Thresholds"
        subtitle="Fine-tune mathematical threshold triggers for each risk taxonomy category"
        action={
          <Button variant="outline" size="sm" type="button" onClick={handleRestoreDefaults}>
            <RefreshCw className="w-3.5 h-3.5" />
            Restore Defaults
          </Button>
        }
      />

      <form onSubmit={handleSave} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(values).map(([name, val]) => {
            const readable = name.replace(/_/g, " ");
            const isPercent = name.includes("rate") || name.includes("ratio") || name.includes("threshold") && !name.includes("days");

            return (
              <div
                key={name}
                className="p-3.5 rounded-xl border border-zinc-800 bg-zinc-950/60 flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-semibold text-zinc-200 capitalize">
                    {readable}
                  </label>
                  <span className="font-mono text-xs font-bold text-indigo-400">
                    {isPercent ? `${Math.round(val * 100)}%` : `${val} days`}
                  </span>
                </div>

                <input
                  type="number"
                  step={isPercent ? "0.05" : "1"}
                  min="0"
                  max={isPercent ? "1.0" : "180"}
                  value={val}
                  onChange={(e) => handleChange(name, parseFloat(e.target.value) || 0)}
                  className="w-full px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-100 focus:outline-none focus:border-indigo-500"
                />
              </div>
            );
          })}
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-zinc-800">
          {savedMessage ? (
            <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
              <Check className="w-4 h-4" /> Thresholds updated successfully!
            </span>
          ) : (
            <span className="text-xs text-zinc-400">
              Changes apply on the next deterministic evaluation cycle.
            </span>
          )}

          <Button variant="primary" size="md" type="submit" isLoading={isSaving}>
            Save Custom Thresholds
          </Button>
        </div>
      </form>
    </Card>
  );
}
