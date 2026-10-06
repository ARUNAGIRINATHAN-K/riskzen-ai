import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.work_item import (
    MilestoneCreate,
    MilestoneResponse,
    TimelineItemResponse,
)
from app.services.milestone_service import MilestoneService

router = APIRouter(prefix="/projects/{project_id}", tags=["Milestones"])


@router.get(
    "/milestones",
    response_model=list[MilestoneResponse],
    summary="List all milestones for a project with progress statistics",
)
async def list_milestones(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await MilestoneService.list_milestones(db, project_id)


@router.post(
    "/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new milestone",
)
async def create_milestone(
    project_id: uuid.UUID,
    data: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
):
    return await MilestoneService.create_milestone(db, project_id, data)


@router.get(
    "/milestones/{milestone_id}",
    response_model=MilestoneResponse,
    summary="Get milestone detail",
)
async def get_milestone(
    project_id: uuid.UUID,
    milestone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    ms = await MilestoneService.get_milestone(db, project_id, milestone_id)
    if not ms:
        raise HTTPException(status_code=404, detail="Milestone not found")
    return ms


@router.get(
    "/timeline",
    response_model=list[TimelineItemResponse],
    summary="Get chronological milestone timeline with assigned work items and risk status",
)
async def get_timeline(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    return await MilestoneService.get_timeline(db, project_id)
