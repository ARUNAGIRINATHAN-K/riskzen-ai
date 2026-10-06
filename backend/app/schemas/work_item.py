import uuid
from datetime import date, datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


# ── Milestone Schemas ──

class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    target_date: Optional[date] = None
    status: str = Field(default="open", description="open or closed")


class MilestoneCreate(MilestoneBase):
    external_id: Optional[str] = None


class MilestoneUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[date] = None
    status: Optional[str] = None
    completion_percent: Optional[float] = None


class MilestoneResponse(MilestoneBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    external_id: Optional[str] = None
    completion_percent: float = 0.0
    created_at: datetime
    updated_at: datetime
    work_items_count: int = 0
    completed_items_count: int = 0


# ── Work Item Schemas ──

class WorkItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    status: str = Field(default="open", description="open, in_progress, done, closed")
    priority: str = Field(default="medium", description="low, medium, high, critical")
    item_type: str = Field(default="task", description="task, bug, feature, decision, pull_request")
    assignee: Optional[str] = None
    labels: list[str] = Field(default_factory=list)
    due_date: Optional[date] = None


class WorkItemCreate(WorkItemBase):
    external_id: Optional[str] = None
    source_type: str = "github"
    milestone_id: Optional[uuid.UUID] = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class WorkItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    item_type: Optional[str] = None
    assignee: Optional[str] = None
    labels: Optional[list[str]] = None
    due_date: Optional[date] = None
    milestone_id: Optional[uuid.UUID] = None
    completed_at: Optional[datetime] = None
    cycle_time_hours: Optional[float] = None


class WorkItemResponse(WorkItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    milestone_id: Optional[uuid.UUID] = None
    external_id: Optional[str] = None
    source_type: str
    completed_at: Optional[datetime] = None
    cycle_time_hours: Optional[float] = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


# ── Dependency Schemas ──

class DependencyCreate(BaseModel):
    source_item_id: uuid.UUID = Field(..., description="The blocked work item ID")
    target_item_id: uuid.UUID = Field(..., description="The prerequisite blocker work item ID")
    dependency_type: str = Field(default="blocks", description="blocks, depends_on, related")


class DependencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    source_item_id: uuid.UUID
    target_item_id: uuid.UUID
    dependency_type: str
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    source_item_title: Optional[str] = None
    target_item_title: Optional[str] = None


# ── Timeline Schemas ──

class TimelineItemResponse(BaseModel):
    milestone: MilestoneResponse
    work_items: list[WorkItemResponse] = Field(default_factory=list)
    blocked_count: int = 0
    at_risk: bool = False
