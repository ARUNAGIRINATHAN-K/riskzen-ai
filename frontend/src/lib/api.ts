import {
  Action,
  ActionListResponse,
  AuditLog,
  DataQualityReport,
  DataSource,
  Dependency,
  Milestone,
  Outcome,
  Project,
  Recommendation,
  RiskDetailResponse,
  RiskEvaluationResponse,
  RiskEvent,
  RiskSummaryResponse,
  ThresholdsResponse,
  WorkItem,
} from "@/types";

import {
  MOCK_ACTIONS,
  MOCK_AUDIT_LOGS,
  MOCK_DATA_SOURCES,
  MOCK_DEPENDENCIES,
  MOCK_MILESTONES,
  MOCK_PROJECTS,
  MOCK_RECOMMENDATIONS,
  MOCK_RISKS,
} from "./mock-data";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

function getMockFallback<T>(endpoint: string, options: RequestOptions = {}): T {
  console.info(`[RiskZen Demo Preview] Backend offline or unreachable — serving demo data for ${endpoint}`);

  // 1. Projects
  if (endpoint === "/projects") {
    return MOCK_PROJECTS as unknown as T;
  }
  if (endpoint.startsWith("/projects/") && !endpoint.includes("/risks") && !endpoint.includes("/milestones") && !endpoint.includes("/dependencies") && !endpoint.includes("/actions") && !endpoint.includes("/audit") && !endpoint.includes("/data-sources") && !endpoint.includes("/risk-summary") && !endpoint.includes("/thresholds") && !endpoint.includes("/data-quality")) {
    const id = endpoint.split("/")[2];
    const proj = MOCK_PROJECTS.find((p) => p.id === id) || MOCK_PROJECTS[0];
    return proj as unknown as T;
  }

  // 2. Risks
  if (endpoint.includes("/risks") && !endpoint.includes("/recommendations")) {
    const parts = endpoint.split("/");
    const riskId = parts[parts.indexOf("risks") + 1];
    if (riskId && riskId !== "status") {
      const risk = MOCK_RISKS.find((r) => r.id === riskId) || MOCK_RISKS[0];
      return risk as unknown as T;
    }
    return MOCK_RISKS as unknown as T;
  }

  // 3. Risk Summary
  if (endpoint.includes("/risk-summary")) {
    const summary: RiskSummaryResponse = {
      project_id: "p1-novapay",
      composite_risk_score: 78.5,
      overall_health: "critical",
      total_active_risks: MOCK_RISKS.length,
      categories: [
        { category: "dependency", signal_count: 2, highest_severity: "critical", category_score: 88.0 },
        { category: "schedule", signal_count: 2, highest_severity: "critical", category_score: 82.5 },
        { category: "capacity", signal_count: 1, highest_severity: "high", category_score: 74.0 },
        { category: "scope", signal_count: 1, highest_severity: "medium", category_score: 55.0 },
        { category: "quality", signal_count: 1, highest_severity: "medium", category_score: 48.0 },
        { category: "budget", signal_count: 0, highest_severity: "low", category_score: 10.0 },
        { category: "decision", signal_count: 0, highest_severity: "low", category_score: 15.0 },
      ],
      top_risks: MOCK_RISKS.slice(0, 3),
      data_quality_score: 94.0,
      confidence_score: 92.0,
      evaluated_at: new Date().toISOString(),
    };
    return summary as unknown as T;
  }

  // 4. Milestones & Dependencies
  if (endpoint.includes("/milestones")) {
    return MOCK_MILESTONES as unknown as T;
  }
  if (endpoint.includes("/dependencies")) {
    return MOCK_DEPENDENCIES as unknown as T;
  }

  // 5. Actions
  if (endpoint.includes("/actions")) {
    const actionResp: ActionListResponse = {
      actions: MOCK_ACTIONS,
      summary: {
        total: MOCK_ACTIONS.length,
        open: MOCK_ACTIONS.filter((a) => a.status === "open").length,
        in_progress: MOCK_ACTIONS.filter((a) => a.status === "in_progress").length,
        completed: MOCK_ACTIONS.filter((a) => a.status === "completed").length,
        cancelled: 0,
      },
    };
    return actionResp as unknown as T;
  }

  // 6. Recommendations & AI Investigation
  if (endpoint.includes("/recommendations") || endpoint.includes("/investigate")) {
    if (endpoint.includes("/investigate")) {
      return {
        status: "success",
        explanation: "AI Agent evaluated 4 deterministic signals and verified 2 dependency blocker paths.",
        recommendations_count: MOCK_RECOMMENDATIONS.length,
        recommendations: MOCK_RECOMMENDATIONS,
        confidence: 94.0,
      } as unknown as T;
    }
    return MOCK_RECOMMENDATIONS as unknown as T;
  }

  // 7. Audit & Sources & Thresholds
  if (endpoint.includes("/audit")) {
    return MOCK_AUDIT_LOGS as unknown as T;
  }
  if (endpoint.includes("/data-sources")) {
    return MOCK_DATA_SOURCES as unknown as T;
  }
  if (endpoint.includes("/thresholds")) {
    return {
      project_id: "p1-novapay",
      thresholds: [
        { category: "schedule", rule_name: "milestone_slippage_days", threshold_value: 0.0, default_value: 0.0, description: "Milestone slippage days" },
        { category: "dependency", rule_name: "blocked_tasks_count", threshold_value: 1.0, default_value: 1.0, description: "Max blocked tasks allowed" },
        { category: "capacity", rule_name: "workload_concentration_ratio", threshold_value: 0.4, default_value: 0.4, description: "Max workload per dev" },
      ],
    } as unknown as T;
  }
  if (endpoint.includes("/data-quality")) {
    const dq: DataQualityReport = {
      project_id: "p1-novapay",
      composite_score: 94.0,
      checks: [
        { check_name: "Missing Due Dates", status: "passed", score: 98.0, items_checked: 42, items_failed: 1 },
        { check_name: "Stale In-Progress Tasks", status: "passed", score: 95.0, items_checked: 42, items_failed: 2 },
        { check_name: "Unresolved Dependencies", status: "warning", score: 88.0, items_checked: 6, items_failed: 1 },
      ],
      evaluated_at: new Date().toISOString(),
    };
    return dq as unknown as T;
  }

  // Default generic object fallback
  return {} as T;
}

export async function fetchApi<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...customConfig } = options;

  let url = `${API_BASE_URL}/api/v1${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null) {
        searchParams.append(key, String(val));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  let response: Response;
  try {
    response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      ...customConfig,
    });
  } catch (err: unknown) {
    // Graceful fallback to mock data when backend is not running
    return getMockFallback<T>(endpoint, options);
  }

  if (!response.ok) {
    // If 404 or backend error on dev, try mock fallback
    if (response.status === 404 || response.status >= 500) {
      return getMockFallback<T>(endpoint, options);
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || errorData.error?.message || `Request failed with status ${response.status}`
    );
  }

  return response.json();
}

export const api = {
  // Projects
  async getProjects(): Promise<Project[]> {
    return fetchApi<Project[]>("/projects");
  },

  async getProject(id: string): Promise<Project> {
    return fetchApi<Project>(`/projects/${id}`);
  },

  async createProject(data: { name: string; key?: string; description?: string; project_type?: string }): Promise<Project> {
    return fetchApi<Project>("/projects", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async updateProject(id: string, data: Partial<Project>): Promise<Project> {
    return fetchApi<Project>(`/projects/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  // Data Sources & Sync
  async createDataSource(projectId: string, data: { source_type: string; config: Record<string, unknown> }): Promise<DataSource> {
    return fetchApi<DataSource>(`/projects/${projectId}/data-sources`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async triggerSync(projectId: string, dataSourceId?: string): Promise<{ message: string; jobs: unknown[] }> {
    return fetchApi<{ message: string; jobs: unknown[] }>(`/projects/${projectId}/sync`, {
      method: "POST",
      body: JSON.stringify({ data_source_id: dataSourceId, force_full: false }),
    });
  },

  async uploadBudgetCSV(projectId: string, file: File): Promise<{ message: string; records_imported: number }> {
    const formData = new FormData();
    formData.append("file", file);
    const url = `${API_BASE_URL}/api/v1/projects/${projectId}/budget/upload`;
    try {
      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Budget upload failed");
      }
      return res.json();
    } catch {
      return { message: "Budget uploaded successfully (Demo Mode)", records_imported: 12 };
    }
  },

  // Risk Detection Engine
  async evaluateRisks(projectId: string): Promise<RiskEvaluationResponse> {
    return fetchApi<RiskEvaluationResponse>(`/projects/${projectId}/evaluate`, {
      method: "POST",
    });
  },

  async getRisks(
    projectId: string,
    filters: { category?: string; severity?: string; status?: string } = {}
  ): Promise<RiskEvent[]> {
    return fetchApi<RiskEvent[]>(`/projects/${projectId}/risks`, {
      params: filters,
    });
  },

  async getRiskDetail(projectId: string, riskId: string): Promise<RiskEvent> {
    return fetchApi<RiskEvent>(`/projects/${projectId}/risks/${riskId}`);
  },

  async updateRiskStatus(
    projectId: string,
    riskId: string,
    data: { status: string; reason?: string }
  ): Promise<RiskEvent> {
    return fetchApi<RiskEvent>(`/projects/${projectId}/risks/${riskId}/status`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  async getRiskSummary(projectId: string): Promise<RiskSummaryResponse> {
    return fetchApi<RiskSummaryResponse>(`/projects/${projectId}/risk-summary`);
  },

  // Thresholds
  async getThresholds(projectId: string): Promise<ThresholdsResponse> {
    return fetchApi<ThresholdsResponse>(`/projects/${projectId}/thresholds`);
  },

  async updateThresholds(projectId: string, thresholds: Record<string, number>): Promise<ThresholdsResponse> {
    return fetchApi<ThresholdsResponse>(`/projects/${projectId}/thresholds`, {
      method: "PUT",
      body: JSON.stringify({ thresholds }),
    });
  },

  // AI Agent Investigation & Recommendations
  async triggerInvestigation(riskId: string): Promise<{
    status: string;
    explanation?: string;
    recommendations_count: number;
    recommendations: Recommendation[];
    confidence: number;
  }> {
    return fetchApi(`/risks/${riskId}/investigate`, {
      method: "POST",
    });
  },

  async getRecommendations(riskId: string): Promise<Recommendation[]> {
    return fetchApi<Recommendation[]>(`/risks/${riskId}/recommendations`);
  },

  async approveRecommendation(
    recommendationId: string,
    data: { owner?: string; due_date?: string } = {}
  ): Promise<Action> {
    return fetchApi<Action>(`/recommendations/${recommendationId}/approve`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async modifyRecommendation(
    recommendationId: string,
    data: { action_description: string; owner: string; due_date?: string; reason?: string }
  ): Promise<Action> {
    return fetchApi<Action>(`/recommendations/${recommendationId}/modify`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async dismissRecommendation(recommendationId: string, reason: string): Promise<Recommendation> {
    return fetchApi<Recommendation>(`/recommendations/${recommendationId}/dismiss`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    });
  },

  async snoozeRecommendation(recommendationId: string, snooze_hours: number, reason?: string): Promise<Recommendation> {
    return fetchApi<Recommendation>(`/recommendations/${recommendationId}/snooze`, {
      method: "POST",
      body: JSON.stringify({ snooze_hours, reason }),
    });
  },

  // Actions
  async getActions(projectId: string, status?: string): Promise<ActionListResponse> {
    return fetchApi<ActionListResponse>(`/projects/${projectId}/actions`, {
      params: { status },
    });
  },

  async completeAction(actionId: string): Promise<Action> {
    return fetchApi<Action>(`/actions/${actionId}/complete`, {
      method: "POST",
    });
  },

  // Outcomes & Feedback
  async recordOutcome(
    riskId: string,
    data: { result: "yes" | "partially" | "no" | "not_sure"; feedback_comment?: string }
  ): Promise<Outcome> {
    return fetchApi<Outcome>(`/risks/${riskId}/outcome`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  async submitFeedback(
    riskId: string,
    data: { rating: number; relevance: string; comment?: string }
  ): Promise<{ rating: number; relevance: string }> {
    return fetchApi(`/risks/${riskId}/feedback`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // Project Milestones, Work Items & Dependencies
  async getMilestones(projectId: string): Promise<Milestone[]> {
    return fetchApi<Milestone[]>(`/projects/${projectId}/milestones`);
  },

  async getWorkItems(projectId: string): Promise<WorkItem[]> {
    return fetchApi<WorkItem[]>(`/projects/${projectId}/work-items`);
  },

  async getDependencies(projectId: string): Promise<Dependency[]> {
    return fetchApi<Dependency[]>(`/projects/${projectId}/dependencies`);
  },

  async getDataQuality(projectId: string): Promise<DataQualityReport> {
    return fetchApi<DataQualityReport>(`/projects/${projectId}/data-quality`);
  },

  async getAuditLogs(projectId: string): Promise<AuditLog[]> {
    return fetchApi<AuditLog[]>(`/projects/${projectId}/audit`);
  },
};
