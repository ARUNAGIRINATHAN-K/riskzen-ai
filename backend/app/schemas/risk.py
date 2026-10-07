import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class RiskSignalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_event_id: uuid.UUID
    signal_type: str
    category: str
    value: float
    threshold: float
    severity: str
    details: dict[str, Any]
    detected_at: datetime


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_event_id: uuid.UUID
    source_type: str
    reference_id: Optional[uuid.UUID] = None
    reference_label: str
    explanation: str
    relevance_score: float
    created_at: datetime


class RiskHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    risk_event_id: uuid.UUID
    severity: str
    score: float
    status: str
    details: dict[str, Any]
    recorded_at: datetime


class RiskEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    affected_milestone_id: Optional[uuid.UUID] = None
    category: str
    title: str
    description: Optional[str] = None
    severity: str
    confidence: str
    score: float
    status: str
    detected_at: datetime
    updated_at: datetime
    agent_explanation: Optional[str] = None
    agent_investigated_at: Optional[datetime] = None


class RiskDetailResponse(RiskEventResponse):
    signals: list[RiskSignalResponse] = Field(default_factory=list)
    evidence_items: list[EvidenceResponse] = Field(default_factory=list)
    history: list[RiskHistoryResponse] = Field(default_factory=list)


class RiskStatusUpdate(BaseModel):
    status: str = Field(..., description="new, active, mitigated, resolved, closed, dismissed")
    reason: Optional[str] = Field(None, description="Optional note explaining PM status change")


class RiskCategorySummary(BaseModel):
    category: str
    score: float
    severity: str
    active_risks_count: int
    signals_count: int
    trend: str = Field(default="stable", description="increasing, stable, decreasing")


class RiskSummaryResponse(BaseModel):
    project_id: uuid.UUID
    overall_score: float
    overall_severity: str
    overall_confidence: str
    active_risks_total: int
    critical_risks_total: int
    categories: list[RiskCategorySummary]
    evaluated_at: datetime


class RiskEvaluationResponse(BaseModel):
    project_id: uuid.UUID
    signals_detected: int
    events_created: int
    events_updated: int
    overall_score: float
    overall_severity: str
    evaluated_at: datetime
