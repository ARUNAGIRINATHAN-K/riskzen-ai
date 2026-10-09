import React from "react";
import { Activity, Bot, Check, CheckCircle, Shield, Sliders, X } from "@/components/icons";
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
        return <Check className="w-3.5 h-3.5 text-pulse-green" />;
      case "recommendation_modified":
        return <Sliders className="w-3.5 h-3.5 text-signal-teal" />;
      case "recommendation_dismissed":
        return <X className="w-3.5 h-3.5 text-coral-red" />;
      case "risk_investigated":
        return <Bot className="w-3.5 h-3.5 text-iris-violet" />;
      case "action_completed":
        return <CheckCircle className="w-3.5 h-3.5 text-pulse-green" />;
      case "outcome_recorded":
        return <Shield className="w-3.5 h-3.5 text-acid-lime" />;
      default:
        return <Activity className="w-3.5 h-3.5 text-fog" />;
    }
  };

  return (
    <Card>
      <CardHeader
        title="Chronological Governance & Audit Log"
        subtitle="Immutable ledger of all AI risk detections, human PM approvals, and mitigation outcomes"
      />

      {logs.length === 0 ? (
        <p className="text-caption text-fog py-6 text-center">
          No audit entries recorded yet.
        </p>
      ) : (
        <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-[1px] before:bg-graphite">
          {logs.map((log) => (
            <div key={log.id} className="relative group">
              {/* Dot icon */}
              <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-carbon border border-graphite flex items-center justify-center shrink-0">
                {getEventIcon(log.event_type)}
              </div>

              <div className="p-3 rounded-[6px] border border-graphite bg-void space-y-1">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="text-caption font-[510] text-mist uppercase tracking-wide">
                      {log.event_type.replace(/_/g, " ")}
                    </span>
                    <Badge variant="outline" size="sm">
                      by {log.actor || "System"}
                    </Badge>
                  </div>
                  <span className="text-micro text-fog font-mono">
                    {formatDateTime(log.created_at)}
                  </span>
                </div>

                {log.details && (
                  <div className="pt-1 text-caption text-fog">
                    {Object.entries(log.details).map(([k, v]) => (
                      <div key={k} className="flex items-start gap-1.5 text-micro">
                        <span className="text-ash capitalize">{k.replace(/_/g, " ")}:</span>
                        <span className="text-mist font-[510] truncate max-w-lg">
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
