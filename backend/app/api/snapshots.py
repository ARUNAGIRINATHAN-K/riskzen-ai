import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.snapshot import ProjectSnapshotResponse
from app.services.snapshot_service import SnapshotService

router = APIRouter(prefix="/projects/{project_id}/snapshots", tags=["Snapshots"])


@router.get(
    "",
    response_model=list[ProjectSnapshotResponse],
    summary="List historical state snapshots for a project",
)
async def list_snapshots(
    project_id: uuid.UUID,
    limit: int = Query(default=30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await SnapshotService.list_snapshots(db, project_id, limit=limit)


@router.post(
    "",
    response_model=ProjectSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Capture a point-in-time snapshot of the current project state",
)
async def capture_snapshot(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await SnapshotService.capture_snapshot(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
