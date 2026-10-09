import React from "react";
import { Activity, Bot, Check, CheckCircle, FileText, Layers, Shield, Sliders, X } from "@/components/icons";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { formatDateTime } from "@/lib/utils";
import { AuditLog } from "@/types";

interface AuditTimelineProps {
  logs: AuditLog[];
}

export function AuditTimeline({ logs }: AuditTimelineProps) {
  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case "recommendation_approved":
        return <Check className="w-4 h-4 text-emerald-400" />;
      case "recommendation_modified":
        return <Sliders className="w-4 h-4 text-sky-400" />;
      case "recommendation_dismissed":
        return <X className="w-4 h-4 text-rose-400" />;
      case "risk_investigated":
        return <Bot className="w-4 h-4 text-purple-400" />;
      case "action_completed":
        return <CheckCircle className="w-4 h-4 text-emerald-400" />;
      case "outcome_recorded":
        return <Shield className="w-4 h-4 text-indigo-400" />;
      default:
        return <Activity className="w-4 h-4 text-zinc-400" />;
    }
  };

  return (
    <Card>
      <CardHeader
        title="Chronological Governance & Audit Log"
        subtitle="Immutable ledger of all AI risk detections, human PM approvals, and mitigation outcomes"
      />

      {logs.length === 0 ? (
        <p className="text-xs text-zinc-400 py-6 text-center">
          No audit entries recorded yet.
        </p>
      ) : (
        <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-zinc-800">
          {logs.map((log) => (
            <div key={log.id} className="relative group">
              {/* Dot icon */}
              <div className="absolute -left-6 top-0.5 w-6 h-6 rounded-full bg-zinc-900 border border-zinc-700 flex items-center justify-center shrink-0">
                {getEventIcon(log.event_type)}
              </div>

              <div className="p-3.5 rounded-xl border border-zinc-800/80 bg-zinc-950/60 space-y-1.5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-zinc-100 uppercase tracking-wide">
                      {log.event_type.replace(/_/g, " ")}
                    </span>
                    <Badge variant="outline" size="sm">
                      by {log.actor || "System"}
                    </Badge>
                  </div>
                  <span className="text-[11px] text-zinc-500 font-mono">
                    {formatDateTime(log.created_at)}
                  </span>
                </div>

                {log.details && (
                  <div className="pt-1 text-xs text-zinc-400">
                    {Object.entries(log.details).map(([k, v]) => (
                      <div key={k} className="flex items-start gap-1.5 text-[11px]">
                        <span className="text-zinc-500 capitalize">{k.replace(/_/g, " ")}:</span>
                        <span className="text-zinc-300 font-medium truncate max-w-lg">
                          {typeof v === "object" ? JSON.stringify(v) : String(v)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}
