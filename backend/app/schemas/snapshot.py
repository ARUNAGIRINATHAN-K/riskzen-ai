import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class SnapshotCreate(BaseModel):
    note: str | None = None


class ProjectSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    snapshot_date: datetime
    health: str
    metrics_summary: dict[str, Any]
    state_json: dict[str, Any]
    created_at: datetime
