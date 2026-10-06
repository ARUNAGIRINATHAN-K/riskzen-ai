import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Data Source Schemas ──

class DataSourceBase(BaseModel):
    source_type: str = Field(..., description="Source type, e.g. 'github', 'csv_budget'")
    config: dict[str, Any] = Field(default_factory=dict, description="Connection parameters")


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(BaseModel):
    config: Optional[dict[str, Any]] = None
    status: Optional[str] = None


class DataSourceResponse(DataSourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime


# ── Project Schemas ──

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Detailed project description")
    project_type: str = Field(default="software", max_length=50, description="Project domain type")


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[str] = Field(None, description="active, paused, archived")
    health: Optional[str] = Field(None, description="green, yellow, orange, red")


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    health: str
    created_at: datetime
    updated_at: datetime
    data_sources: list[DataSourceResponse] = Field(default_factory=list)


class ProjectSummaryCounts(BaseModel):
    total_work_items: int = 0
    open_work_items: int = 0
    in_progress_work_items: int = 0
    completed_work_items: int = 0
    total_milestones: int = 0
    open_milestones: int = 0
    total_dependencies: int = 0
    active_blockers: int = 0
    active_risks_count: int = 0
    critical_risks_count: int = 0
    data_quality_score: float = 100.0


class ProjectSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project: ProjectResponse
    counts: ProjectSummaryCounts
    last_synced_at: Optional[datetime] = None
