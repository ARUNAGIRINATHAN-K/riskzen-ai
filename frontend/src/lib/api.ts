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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
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
    const errorMsg = err instanceof Error ? err.message : String(err);
    throw new Error(
      `Unable to reach RiskZen API at ${API_BASE_URL}. Please ensure the backend server is running (e.g., 'docker compose up' or 'uvicorn app.main:app --reload --port 8000'). Original error: ${errorMsg}`
    );
  }

  if (!response.ok) {
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
    const res = await fetch(url, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Budget upload failed");
    }
    return res.json();
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
};
