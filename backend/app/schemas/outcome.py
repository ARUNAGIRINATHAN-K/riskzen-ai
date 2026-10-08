"""Pydantic Schemas for Risk Outcomes and Feedback."""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class OutcomeCreate(BaseModel):
    result: str = Field(..., description="yes | partially | no | not_sure")
    feedback_comment: Optional[str] = None


class OutcomeResponse(BaseModel):
    id: uuid.UUID
    risk_event_id: uuid.UUID
    result: str
    feedback_comment: Optional[str] = None
    recorded_at: datetime

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="1 (poor) to 5 (excellent)")
    relevance: str = Field(default="relevant", description="relevant | not_relevant | incorrect | outdated")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    risk_event_id: uuid.UUID
    rating: int
    relevance: str
    comment: Optional[str] = None
    recorded_at: datetime
