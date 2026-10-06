import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class BudgetRecordBase(BaseModel):
    period: str = Field(..., description="e.g. '2026-10', '2026-Q4'")
    category: str = Field(..., description="e.g. 'Engineering', 'Infrastructure'")
    planned_amount: float = Field(default=0.0, ge=0.0)
    actual_amount: float = Field(default=0.0, ge=0.0)
    currency: str = Field(default="USD", max_length=10)


class BudgetRecordCreate(BudgetRecordBase):
    pass


class BudgetRecordResponse(BudgetRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    variance: float
    source_filename: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BudgetSummaryResponse(BaseModel):
    total_planned: float
    total_actual: float
    total_variance: float
    currency: str = "USD"
    periods_count: int
    categories: list[str]
    records: list[BudgetRecordResponse]
