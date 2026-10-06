import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.work_item import DependencyCreate, DependencyResponse
from app.services.dependency_service import DependencyService

router = APIRouter(prefix="/projects/{project_id}/dependencies", tags=["Dependencies"])


@router.get(
    "",
    response_model=list[DependencyResponse],
    summary="List all cross-item dependencies for a project",
)
async def list_dependencies(
    project_id: uuid.UUID,
    status: Optional[str] = Query(None, description="Filter by active or resolved"),
    db: AsyncSession = Depends(get_db),
):
    return await DependencyService.list_dependencies(db, project_id, status=status)


@router.post(
    "",
    response_model=DependencyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Declare a dependency relationship between two work items",
)
async def create_dependency(
    project_id: uuid.UUID,
    data: DependencyCreate,
    db: AsyncSession = Depends(get_db),
):
    return await DependencyService.create_dependency(db, project_id, data)


@router.patch(
    "/{dependency_id}/resolve",
    response_model=DependencyResponse,
    summary="Mark a dependency as resolved",
)
async def resolve_dependency(
    project_id: uuid.UUID,
    dependency_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    resolved = await DependencyService.resolve_dependency(db, project_id, dependency_id)
    if not resolved:
        raise HTTPException(status_code=404, detail="Dependency not found")
    return resolved
