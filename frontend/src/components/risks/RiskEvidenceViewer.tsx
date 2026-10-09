import React from "react";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { getSeverityBadge } from "@/lib/utils";
import { RiskSignal } from "@/types";

interface RiskEvidenceViewerProps {
  signals?: RiskSignal[];
}

export function RiskEvidenceViewer({ signals = [] }: RiskEvidenceViewerProps) {
  return (
    <Card>
      <CardHeader
        title="Supporting Telemetry & Evidence Trail"
        subtitle="Deterministic rule signals and verified raw database items"
      />

      {signals.length === 0 ? (
        <p className="text-caption text-fog py-4 text-center">
          No secondary signals attached to this risk event.
        </p>
      ) : (
        <div className="space-y-3">
          {signals.map((signal) => {
            const badge = getSeverityBadge(signal.severity);

            return (
              <div
                key={signal.id}
                className="p-4 rounded-[6px] border border-graphite bg-void space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-caption font-[510] text-mist">
                      {signal.rule_id}
                    </span>
                    <span className="text-ash">•</span>
                    <span className="text-caption text-fog font-normal">
                      {signal.signal_type}
                    </span>
                  </div>

                  <Badge variant={signal.severity} size="sm">
                    {signal.severity} ({Math.round(signal.score * 100)}%)
                  </Badge>
                </div>

                <p className="text-caption text-mist leading-relaxed">
                  {signal.description}
                </p>

                {/* Evidence items */}
                {signal.evidence && signal.evidence.length > 0 && (
                  <div className="pt-2 border-t border-graphite space-y-2">
                    <span className="text-micro font-[510] uppercase text-fog block">
                      Captured Work Items & Entities:
                    </span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {signal.evidence.map((ev) => (
                        <div
                          key={ev.id}
                          className="p-2.5 rounded-[6px] bg-carbon border border-graphite text-caption text-mist space-y-1"
                        >
                          <div className="flex items-center justify-between text-micro text-fog font-mono">
                            <span className="uppercase">{ev.source_type}</span>
                            <span className="truncate max-w-[120px]">{ev.source_id}</span>
                          </div>
                          <p className="font-[510] text-paper">{ev.description}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}
