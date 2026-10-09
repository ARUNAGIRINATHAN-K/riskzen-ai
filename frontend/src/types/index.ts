export type ProjectHealth = "green" | "yellow" | "orange" | "red";
export type ProjectStatus = "active" | "paused" | "archived";
export type DataSourceType = "github" | "csv_budget";
export type DataSourceStatus = "connected" | "syncing" | "error" | "disconnected";

export interface DataSource {
  id: string;
  project_id: string;
  source_type: DataSourceType;
  config: Record<string, unknown>;
  status: DataSourceStatus;
  last_synced_at: string | null;
  created_at: string;
}

export interface ProjectSettings {
  planned_budget?: number;
  actual_spend?: number;
  last_evaluated_at?: string;
  overall_risk_score?: number;
  overall_risk_level?: string;
  risk_confidence?: number;
  [key: string]: unknown;
}

export interface Project {
  id: string;
  name: string;
  key?: string;
  description: string | null;
  project_type: string;
  status: ProjectStatus;
  health: ProjectHealth;
  settings?: ProjectSettings;
  data_quality_score?: number;
  created_at: string;
  updated_at: string;
  data_sources?: DataSource[];
}

export type RiskCategory =
  | "schedule"
  | "dependency"
  | "scope"
  | "capacity"
  | "quality"
  | "budget"
  | "decision";

export type RiskSeverity = "low" | "medium" | "high" | "critical";
export type RiskStatus =
  | "new"
  | "active"
  | "mitigated"
  | "resolved"
  | "closed"
  | "dismissed";

export interface EvidenceItem {
  id: string;
  source_type: string;
  source_id: string;
  description: string;
  data_payload?: Record<string, unknown>;
  created_at?: string;
}

export interface RiskSignal {
  id: string;
  rule_id: string;
  signal_type: string;
  severity: RiskSeverity;
  score: number;
  confidence: number;
  description: string;
  metadata_json?: Record<string, unknown>;
  evidence: EvidenceItem[];
  created_at?: string;
}

export interface RiskHistoryItem {
  id: string;
  risk_event_id: string;
  previous_status: RiskStatus | null;
  new_status: RiskStatus;
  changed_by: string;
  reason?: string;
  created_at: string;
}

export interface RiskEvent {
  id: string;
  project_id: string;
  category: RiskCategory;
  severity: RiskSeverity;
  propensity_score: number;
  confidence: number;
  status: RiskStatus;
  title: string;
  description: string;
  signal_type: string;
  affected_milestone_id: string | null;
  raw_metrics?: {
    explanation?: string;
    contributing_factors?: Array<{
      factor: string;
      severity: string;
      evidence_citation: string;
      impact: string;
    }>;
    analysis_confidence?: number;
    investigated_at?: string;
    [key: string]: unknown;
  };
  signals?: RiskSignal[];
  history?: RiskHistoryItem[];
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
}

export interface RiskCategorySummary {
  category: string;
  score: number;
  severity: RiskSeverity;
  signal_count: number;
}

export interface RiskSummaryResponse {
  project_id: string;
  overall_score: number;
  overall_severity: RiskSeverity;
  confidence: number;
  total_active_risks: number;
  risks_by_category: Record<string, number>;
  risks_by_severity: Record<string, number>;
  category_summaries: Record<string, RiskCategorySummary>;
  last_evaluated_at: string;
}

export interface RiskEvaluationResponse {
  project_id: string;
  evaluation_time: string;
  overall_score: number;
  overall_severity: RiskSeverity;
  confidence: number;
  category_scores: Record<string, RiskCategorySummary>;
  total_signals: number;
  created_risks_count: number;
  updated_risks_count: number;
  resolved_risks_count: number;
}

export interface Recommendation {
  id: string;
  risk_event_id: string;
  action_description: string;
  rationale: string;
  suggested_owner: string | null;
  urgency: "immediate" | "today" | "this_week" | "optional";
  status: "pending" | "approved" | "modified" | "dismissed" | "snoozed";
  decision_reason?: string | null;
  decided_at?: string | null;
  snooze_until?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Action {
  id: string;
  project_id: string;
  recommendation_id?: string | null;
  description: string;
  owner: string;
  due_date: string | null;
  status: "pending" | "in_progress" | "completed" | "overdue";
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ActionListResponse {
  project_id: string;
  total_actions: number;
  open_actions: number;
  completed_actions: number;
  overdue_actions: number;
  actions: Action[];
}

export interface Outcome {
  id: string;
  risk_event_id: string;
  result: "yes" | "partially" | "no" | "not_sure";
  feedback_comment?: string | null;
  recorded_at: string;
}

export interface AuditLog {
  id: string;
  project_id: string;
  event_type: string;
  entity_type: string;
  entity_id: string;
  actor: string;
  details?: Record<string, unknown>;
  created_at: string;
}

export interface ThresholdItem {
  name: string;
  value: number;
  description?: string;
}

export interface ThresholdsResponse {
  project_id: string;
  thresholds: ThresholdItem[];
}

export interface Milestone {
  id: string;
  project_id: string;
  external_id?: string | null;
  title: string;
  description?: string | null;
  start_date?: string | null;
  due_date?: string | null;
  status: string;
  progress_percentage?: number;
  total_work_items?: number;
  completed_work_items?: number;
  open_work_items?: number;
}

export interface WorkItem {
  id: string;
  project_id: string;
  milestone_id?: string | null;
  external_id?: string | null;
  title: string;
  description?: string | null;
  status: string;
  priority?: string | null;
  item_type?: string | null;
  story_points?: number | null;
  assignee_id?: string | null;
  due_date?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface Dependency {
  id: string;
  source_item_id: string;
  target_item_id: string;
  dependency_type: string;
  created_at?: string;
  source_item?: WorkItem;
  target_item?: WorkItem;
}

export interface DataQualityReport {
  project_id: string;
  overall_score: number;
  evaluated_at: string;
  checks: Array<{
    id: string;
    check_type: string;
    score: number;
    issues_found: number;
    details?: Record<string, unknown>;
  }>;
}
