import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class ManualSyncRequest(BaseModel):
    data_source_id: Optional[uuid.UUID] = Field(None, description="Specific data source ID to sync; null to sync all")
    force_full_sync: bool = Field(default=False, description="Whether to bypass incremental sync window")


class SyncJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    data_source_id: uuid.UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    items_synced: int
    error_message: Optional[str] = None
    details: dict[str, Any]


class SyncSummaryResponse(BaseModel):
    project_id: uuid.UUID
    jobs_triggered: int
    jobs: list[SyncJobResponse]
