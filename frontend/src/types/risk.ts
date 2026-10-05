export type RiskCategory =
  | "schedule"
  | "dependency"
  | "scope"
  | "capacity"
  | "quality"
  | "budget"
  | "decision";

export type RiskSeverity = "low" | "medium" | "high" | "critical";
export type RiskConfidence = "low" | "medium" | "high";
export type RiskStatus =
  | "new"
  | "active"
  | "mitigated"
  | "resolved"
  | "closed"
  | "dismissed";

export interface RiskEvent {
  id: string;
  project_id: string;
  category: RiskCategory;
  title: string;
  severity: RiskSeverity;
  confidence: RiskConfidence;
  score: number;
  status: RiskStatus;
  affected_milestone_id: string | null;
  detected_at: string;
  updated_at: string;
  agent_explanation: string | null;
  agent_investigated_at: string | null;
}
