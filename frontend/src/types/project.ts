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

export interface Project {
  id: string;
  name: string;
  description: string | null;
  project_type: string;
  status: ProjectStatus;
  health: ProjectHealth;
  created_at: string;
  updated_at: string;
  data_sources?: DataSource[];
}

export interface ProjectCreateInput {
  name: string;
  description?: string;
  project_type?: string;
}

export interface ProjectUpdateInput {
  name?: string;
  description?: string;
  project_type?: string;
  status?: ProjectStatus;
  health?: ProjectHealth;
}
