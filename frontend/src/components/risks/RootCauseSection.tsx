import React from "react";
import { Bot, Shield, Sparkles } from "@/components/icons";
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
    <Card className="border-graphite bg-carbon rounded-[12px] p-6 shadow-sm">
      <CardHeader
        title={
          <div className="flex items-center gap-2">
            <Bot className="w-4 h-4 text-acid-lime" />
            <span>AI Agent Investigation & Root Cause</span>
            <Badge variant="lime" size="sm">
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
            >
              <Sparkles className="w-3.5 h-3.5 text-acid-lime" />
              Re-Investigate
            </Button>
          )
        }
      />

      {/* Narrative Explanation */}
      <div className="p-4 rounded-[6px] bg-void border border-graphite mb-5">
        <span className="text-micro font-[510] text-mist uppercase tracking-wider block mb-1">
          Executive Synthesis
        </span>
        <p className="text-body-sm text-paper leading-relaxed font-normal">
          {explanation}
        </p>
      </div>

      {/* Contributing Factors with Evidence Citations */}
      <div>
        <h4 className="text-micro font-[510] text-fog uppercase tracking-wider mb-3">
          Contributing Factors & Telemetry Citations ({contributingFactors.length})
        </h4>

        {contributingFactors.length === 0 ? (
          <p className="text-caption text-fog py-3">
            Primary factor: Telemetry signal detected by {risk.signal_type || "rule engine"}.
          </p>
        ) : (
          <div className="space-y-2.5">
            {contributingFactors.map((factor, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-[6px] border border-graphite bg-void space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-caption font-[510] text-mist flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full bg-carbon border border-graphite text-acid-lime text-micro flex items-center justify-center font-mono font-bold">
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

                <p className="text-caption text-fog leading-relaxed pl-6">
                  <span className="text-mist font-[510]">Impact:</span> {factor.impact}
                </p>

                {/* Grounded Citation */}
                <div className="ml-6 p-2 rounded-[6px] bg-carbon border border-graphite text-caption text-mist flex items-start gap-2">
                  <Shield className="w-3.5 h-3.5 text-pulse-green shrink-0 mt-0.5" />
                  <div>
                    <span className="text-micro text-pulse-green font-[510] uppercase block">
                      Verified Evidence Citation
                    </span>
                    <span className="text-caption text-fog">{factor.evidence_citation}</span>
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
