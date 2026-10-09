import React from "react";
import { AlertTriangle, FileText, Layers } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { formatDate, getSeverityBadge } from "@/lib/utils";
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
        <p className="text-xs text-zinc-400 py-4 text-center">
          No secondary signals attached to this risk event.
        </p>
      ) : (
        <div className="space-y-4">
          {signals.map((signal) => {
            const badge = getSeverityBadge(signal.severity);

            return (
              <div
                key={signal.id}
                className="p-4 rounded-xl border border-zinc-800 bg-zinc-950/40 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-semibold text-zinc-200">
                      {signal.rule_id}
                    </span>
                    <span className="text-zinc-500">•</span>
                    <span className="text-xs text-zinc-400 font-medium">
                      {signal.signal_type}
                    </span>
                  </div>

                  <Badge variant={signal.severity} size="sm">
                    {signal.severity} ({Math.round(signal.score * 100)}%)
                  </Badge>
                </div>

                <p className="text-xs text-zinc-300 leading-relaxed">
                  {signal.description}
                </p>

                {/* Evidence items */}
                {signal.evidence && signal.evidence.length > 0 && (
                  <div className="pt-2 border-t border-zinc-800/60 space-y-2">
                    <span className="text-[10px] uppercase font-semibold text-zinc-400 block">
                      Captured Work Items & Entities:
                    </span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {signal.evidence.map((ev) => (
                        <div
                          key={ev.id}
                          className="p-2.5 rounded-lg bg-zinc-900/80 border border-zinc-800/80 text-[11px] text-zinc-300 space-y-1"
                        >
                          <div className="flex items-center justify-between text-[10px] text-zinc-400 font-mono">
                            <span className="uppercase">{ev.source_type}</span>
                            <span className="truncate max-w-[120px]">{ev.source_id}</span>
                          </div>
                          <p className="font-medium text-zinc-200">{ev.description}</p>
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
