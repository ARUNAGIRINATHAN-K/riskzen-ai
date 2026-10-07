import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RiskThresholdItem(BaseModel):
    category: str
    signal_type: str
    warning_threshold: float = Field(..., ge=0.0, description="Value triggering warning severity")
    critical_threshold: float = Field(..., ge=0.0, description="Value triggering critical severity")
    description: Optional[str] = None
    unit: str = "count"


class RiskThresholdUpdate(BaseModel):
    thresholds: list[RiskThresholdItem]


class RiskThresholdsResponse(BaseModel):
    project_id: uuid.UUID
    thresholds: list[RiskThresholdItem]
