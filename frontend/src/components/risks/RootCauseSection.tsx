import React from "react";
import { AlertTriangle, Bot, CheckCircle, Shield, Sparkles } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { RiskEvent } from "@/types";

interface RootCauseSectionProps {
  risk: RiskEvent;
  onReinvestigate?: () => void;
  isInvestigating?: boolean;
}

export function RootCauseSection({
  risk,
  onReinvestigate,
  isInvestigating = false,
}: RootCauseSectionProps) {
  const explanation = risk.raw_metrics?.explanation || risk.description;
  const contributingFactors = risk.raw_metrics?.contributing_factors || [];
  const confidence = Math.round((risk.confidence || 0.85) * 100);

  return (
    <Card className="border-indigo-500/30 bg-gradient-to-br from-indigo-950/20 via-zinc-900/80 to-zinc-900/90">
      <CardHeader
        title={
          <div className="flex items-center gap-2">
            <Bot className="w-5 h-5 text-indigo-400" />
            <span>AI Agent Investigation & Root Cause</span>
            <Badge variant="purple" size="sm">
              <Sparkles className="w-3 h-3" />
              {confidence}% Confidence
            </Badge>
          </div>
        }
        subtitle="LangGraph 5-node reasoning workflow grounded in project telemetry"
        action={
          onReinvestigate && (
            <Button
              variant="outline"
              size="sm"
              onClick={onReinvestigate}
              isLoading={isInvestigating}
              className="text-xs"
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              Re-Investigate
            </Button>
          )
        }
      />

      {/* Narrative Explanation */}
      <div className="p-4 rounded-xl bg-zinc-950/70 border border-zinc-800/80 mb-5">
        <span className="text-[11px] font-semibold text-indigo-400 uppercase tracking-wider block mb-1.5">
          Executive Synthesis
        </span>
        <p className="text-sm text-zinc-200 leading-relaxed font-normal">
          {explanation}
        </p>
      </div>

      {/* Contributing Factors with Evidence Citations */}
      <div>
        <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider mb-3">
          Contributing Factors & Telemetry Citations ({contributingFactors.length})
        </h4>

        {contributingFactors.length === 0 ? (
          <p className="text-xs text-zinc-400 py-3">
            Primary factor: Telemetry signal detected by {risk.signal_type || "rule engine"}.
          </p>
        ) : (
          <div className="space-y-3">
            {contributingFactors.map((factor, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-zinc-800/80 bg-zinc-950/50 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-zinc-100 flex items-center gap-2">
                    <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-400 text-[11px] flex items-center justify-center font-bold">
                      {idx + 1}
                    </span>
                    {factor.factor}
                  </span>

                  <Badge
                    variant={
                      factor.severity === "high"
                        ? "high"
                        : factor.severity === "critical"
                        ? "critical"
                        : "medium"
                    }
                    size="sm"
                  >
                    {factor.severity}
                  </Badge>
                </div>

                <p className="text-xs text-zinc-400 leading-relaxed pl-7">
                  <span className="text-zinc-300 font-medium">Impact:</span> {factor.impact}
                </p>

                {/* Grounded Citation */}
                <div className="ml-7 p-2.5 rounded-lg bg-zinc-900/90 border border-zinc-800 text-[11px] text-zinc-300 flex items-start gap-2">
                  <Shield className="w-3.5 h-3.5 text-indigo-400 shrink-0 mt-0.5" />
                  <div>
                    <span className="text-[10px] text-indigo-400 font-semibold uppercase block">
                      Verified Evidence Citation
                    </span>
                    <span>{factor.evidence_citation}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}
