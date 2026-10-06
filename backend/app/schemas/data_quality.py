import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class DataQualityCheckResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    check_type: str
    status: str  # pass, warn, fail
    score: float
    details: dict[str, Any]
    created_at: datetime


class DataQualityReportResponse(BaseModel):
    project_id: uuid.UUID
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Composite score 0-100%")
    status: str = Field(..., description="healthy, needs_attention, poor")
    checks_passed: int
    checks_warned: int
    checks_failed: int
    evaluated_at: datetime
    checks: list[DataQualityCheckResponse]
