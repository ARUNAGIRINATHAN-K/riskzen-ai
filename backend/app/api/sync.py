import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.sync import ManualSyncRequest, SyncJobResponse, SyncSummaryResponse
from app.services.sync_service import SyncService

router = APIRouter(prefix="/projects/{project_id}", tags=["Sync"])


@router.post(
    "/sync",
    response_model=SyncSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger manual synchronization of external data sources",
)
async def trigger_sync(
    project_id: uuid.UUID,
    req: ManualSyncRequest = ManualSyncRequest(),
    db: AsyncSession = Depends(get_db),
):
    try:
        jobs = await SyncService.execute_sync(
            db,
            project_id=project_id,
            data_source_id=req.data_source_id,
            force_full=req.force_full_sync,
        )
        return SyncSummaryResponse(
            project_id=project_id,
            jobs_triggered=len(jobs),
            jobs=jobs,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/sync-history",
    response_model=list[SyncJobResponse],
    summary="List recent connector sync execution jobs for a project",
)
async def get_sync_history(
    project_id: uuid.UUID,
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await SyncService.get_sync_history(db, project_id, limit=limit)
