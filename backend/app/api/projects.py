import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.project import (
    DataSourceCreate,
    DataSourceResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectSummaryResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new monitored project",
)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.create_project(db, data)


@router.get(
    "",
    response_model=PaginatedResponse[ProjectResponse],
    summary="List projects with optional status/health filter",
)
async def list_projects(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    health: Optional[str] = Query(default=None, description="Filter by green, yellow, orange, red"),
    status: Optional[str] = Query(default=None, description="Filter by active, paused, archived"),
    db: AsyncSession = Depends(get_db),
):
    projects, total = await ProjectService.list_projects(
        db, page=page, per_page=per_page, health=health, status=status
    )
    pages = (total + per_page - 1) // per_page if total > 0 else 0
    return PaginatedResponse(
        items=projects,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    project = await ProjectService.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project metadata or status",
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated = await ProjectService.update_project(db, project_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
)
async def delete_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    deleted = await ProjectService.delete_project(db, project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")
    return None


@router.get(
    "/{project_id}/summary",
    response_model=ProjectSummaryResponse,
    summary="Get aggregated counts and summary stats for a project",
)
async def get_project_summary(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    summary = await ProjectService.get_project_summary(db, project_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Project not found")
    return summary


@router.post(
    "/{project_id}/sources",
    response_model=DataSourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a data source for a project",
)
async def register_data_source(
    project_id: uuid.UUID,
    data: DataSourceCreate,
    db: AsyncSession = Depends(get_db),
):
    source = await ProjectService.register_data_source(db, project_id, data)
    if not source:
        raise HTTPException(status_code=404, detail="Project not found")
    return source


@router.get(
    "/{project_id}/sources",
    response_model=list[DataSourceResponse],
    summary="List all connected data sources for a project",
)
async def list_data_sources(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await ProjectService.list_data_sources(db, project_id)


@router.get(
    "/{project_id}/audit",
    summary="List chronological audit events for a project",
)
async def get_project_audit(
    project_id: uuid.UUID,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.audit import AuditLog

    stmt = (
        select(AuditLog)
        .where(AuditLog.project_id == project_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    res = await db.execute(stmt)
    logs = res.scalars().all()
    return [
        {
            "id": str(log.id),
            "project_id": str(log.project_id),
            "event_type": log.event_type,
            "entity_type": log.entity_type,
            "entity_id": str(log.entity_id) if log.entity_id else "",
            "actor": log.actor,
            "details": log.details,
            "created_at": log.created_at.isoformat() if log.created_at else "",
        }
        for log in logs
    ]

