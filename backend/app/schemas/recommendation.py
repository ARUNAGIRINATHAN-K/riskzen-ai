"""Pydantic Schemas for Recommendations and Agent Investigation."""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationBase(BaseModel):
    action_description: str
    rationale: str
    suggested_owner: Optional[str] = None
    urgency: str = Field(default="this_week", description="immediate | today | this_week | optional")


class RecommendationResponse(RecommendationBase):
    id: uuid.UUID
    risk_event_id: uuid.UUID
    status: str  # pending, approved, modified, dismissed, snoozed
    decision_reason: Optional[str] = None
    decided_at: Optional[datetime] = None
    snooze_until: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecommendationApproveRequest(BaseModel):
    owner: Optional[str] = Field(None, description="Override owner if desired")
    due_date: Optional[str] = Field(None, description="Action target due date (YYYY-MM-DD)")


class RecommendationModifyRequest(BaseModel):
    action_description: str
    rationale: Optional[str] = None
    owner: str
    due_date: Optional[str] = None
    reason: Optional[str] = None


class RecommendationDismissRequest(BaseModel):
    reason: str = Field(..., min_length=3, description="Reason for dismissing recommendation")


class RecommendationSnoozeRequest(BaseModel):
    snooze_hours: int = Field(default=24, ge=1, le=720, description="Hours to snooze recommendation")
    reason: Optional[str] = None


class InvestigationTriggerResponse(BaseModel):
    risk_event_id: uuid.UUID
    project_id: uuid.UUID
    status: str
    explanation: Optional[str] = None
    contributing_factors_count: int = 0
    recommendations_count: int = 0
    recommendations: List[RecommendationResponse] = []
    confidence: float = 0.0
    quality_check_passed: bool = True
