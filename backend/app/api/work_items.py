import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.work_item import WorkItemCreate, WorkItemResponse, WorkItemUpdate
from app.services.work_item_service import WorkItemService

router = APIRouter(prefix="/projects/{project_id}/work-items", tags=["Work Items"])


@router.get(
    "",
    response_model=PaginatedResponse[WorkItemResponse],
    summary="List work items for a project with filters",
)
async def list_work_items(
    project_id: uuid.UUID,
    status: Optional[str] = Query(None, description="Filter by open, in_progress, done, closed"),
    priority: Optional[str] = Query(None, description="Filter by low, medium, high, critical"),
    assignee: Optional[str] = Query(None, description="Filter by assignee username/name"),
    item_type: Optional[str] = Query(None, description="Filter by task, bug, feature, decision, pull_request"),
    milestone_id: Optional[uuid.UUID] = Query(None, description="Filter by milestone ID"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, total = await WorkItemService.list_work_items(
        db,
        project_id=project_id,
        status=status,
        priority=priority,
        assignee=assignee,
        item_type=item_type,
        milestone_id=milestone_id,
        page=page,
        per_page=per_page,
    )
    pages = (total + per_page - 1) // per_page if total > 0 else 0
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.post(
    "",
    response_model=WorkItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new work item manually",
)
async def create_work_item(
    project_id: uuid.UUID,
    data: WorkItemCreate,
    db: AsyncSession = Depends(get_db),
):
    return await WorkItemService.create_work_item(db, project_id, data)


@router.get(
    "/{item_id}",
    response_model=WorkItemResponse,
    summary="Get work item detail",
)
async def get_work_item(
    project_id: uuid.UUID,
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    item = await WorkItemService.get_work_item(db, project_id, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Work item not found")
    return item


@router.patch(
    "/{item_id}",
    response_model=WorkItemResponse,
    summary="Update a work item",
)
async def update_work_item(
    project_id: uuid.UUID,
    item_id: uuid.UUID,
    data: WorkItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    updated = await WorkItemService.update_work_item(db, project_id, item_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Work item not found")
    return updated
