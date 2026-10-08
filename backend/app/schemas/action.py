"""Pydantic Schemas for Action Item Tracking."""
import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ActionBase(BaseModel):
    description: str
    owner: str
    due_date: Optional[date] = None
    status: str = Field(default="pending", description="pending | in_progress | completed | overdue")


class ActionCreate(ActionBase):
    recommendation_id: Optional[uuid.UUID] = None


class ActionUpdate(BaseModel):
    description: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None  # pending, in_progress, completed, overdue


class ActionResponse(ActionBase):
    id: uuid.UUID
    project_id: uuid.UUID
    recommendation_id: Optional[uuid.UUID] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActionListResponse(BaseModel):
    project_id: uuid.UUID
    total_actions: int
    open_actions: int
    completed_actions: int
    overdue_actions: int
    actions: List[ActionResponse]
