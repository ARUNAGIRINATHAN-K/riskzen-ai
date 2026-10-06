import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.work_item import Dependency, Milestone, WorkItem
from app.schemas.work_item import (
    MilestoneCreate,
    MilestoneResponse,
    MilestoneUpdate,
    TimelineItemResponse,
    WorkItemResponse,
)
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.milestone")


class MilestoneService:
    """Service handling milestone CRUD, recalculating progress, and timeline mapping."""

    @staticmethod
    async def create_milestone(
        session: AsyncSession,
        project_id: uuid.UUID,
        data: MilestoneCreate,
    ) -> MilestoneResponse:
        """Create a new milestone."""
        ms = Milestone(
            project_id=project_id,
            external_id=data.external_id,
            title=data.title,
            description=data.description,
            target_date=data.target_date,
            status=data.status,
            completion_percent=0.0,
        )
        session.add(ms)
        await session.commit()
        await session.refresh(ms)
        return MilestoneResponse.model_validate(ms)

    @staticmethod
    async def upsert_milestone(
        session: AsyncSession,
        project_id: uuid.UUID,
        milestone_data: dict,
    ) -> tuple[Milestone, bool]:
        """Upsert a milestone using external_id or title for deduplication."""
        ext_id = milestone_data.get("external_id")
        title = milestone_data.get("title")

        existing = None
        if ext_id:
            stmt = select(Milestone).where(
                Milestone.project_id == project_id,
                Milestone.external_id == ext_id,
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

        if not existing and title:
            stmt = select(Milestone).where(
                Milestone.project_id == project_id,
                Milestone.title == title,
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

        is_created = False
        if existing:
            for key in ["title", "description", "target_date", "status", "completion_percent"]:
                if key in milestone_data and milestone_data[key] is not None:
                    setattr(existing, key, milestone_data[key])
            if ext_id and not existing.external_id:
                existing.external_id = ext_id
            existing.updated_at = datetime.now(timezone.utc)
            ms = existing
        else:
            ms = Milestone(
                project_id=project_id,
                external_id=ext_id,
                title=title or "Untitled Milestone",
                description=milestone_data.get("description"),
                target_date=milestone_data.get("target_date"),
                status=milestone_data.get("status", "open"),
                completion_percent=milestone_data.get("completion_percent", 0.0),
            )
            session.add(ms)
            is_created = True

        await session.flush()
        return ms, is_created

    @staticmethod
    async def list_milestones(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> list[MilestoneResponse]:
        """List all milestones for a project with computed work item stats."""
        stmt = (
            select(Milestone)
            .options(selectinload(Milestone.work_items))
            .where(Milestone.project_id == project_id)
            .order_by(Milestone.target_date.asc().nulls_last())
        )
        result = await session.execute(stmt)
        milestones = result.scalars().all()

        responses = []
        for ms in milestones:
            items = ms.work_items or []
            total_items = len(items)
            completed_items = sum(1 for i in items if i.status in ["done", "closed"])
            comp_pct = round((completed_items / total_items) * 100.0, 1) if total_items > 0 else ms.completion_percent

            resp = MilestoneResponse.model_validate(ms)
            resp.completion_percent = comp_pct
            resp.work_items_count = total_items
            resp.completed_items_count = completed_items
            responses.append(resp)

        return responses

    @staticmethod
    async def get_milestone(
        session: AsyncSession,
        project_id: uuid.UUID,
        milestone_id: uuid.UUID,
    ) -> Optional[MilestoneResponse]:
        """Get milestone by ID with computed stats."""
        stmt = (
            select(Milestone)
            .options(selectinload(Milestone.work_items))
            .where(Milestone.id == milestone_id, Milestone.project_id == project_id)
        )
        result = await session.execute(stmt)
        ms = result.scalar_one_or_none()
        if not ms:
            return None

        items = ms.work_items or []
        total_items = len(items)
        completed_items = sum(1 for i in items if i.status in ["done", "closed"])
        comp_pct = round((completed_items / total_items) * 100.0, 1) if total_items > 0 else ms.completion_percent

        resp = MilestoneResponse.model_validate(ms)
        resp.completion_percent = comp_pct
        resp.work_items_count = total_items
        resp.completed_items_count = completed_items
        return resp

    @staticmethod
    async def get_timeline(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> list[TimelineItemResponse]:
        """Generate milestone timeline mapping with assigned work items and risk status."""
        milestone_responses = await MilestoneService.list_milestones(session, project_id)

        timeline = []
        for ms_resp in milestone_responses:
            # Fetch work items for this milestone
            wi_stmt = (
                select(WorkItem)
                .where(WorkItem.milestone_id == ms_resp.id, WorkItem.project_id == project_id)
                .order_by(WorkItem.status.asc(), WorkItem.priority.desc())
            )
            wi_res = await session.execute(wi_stmt)
            work_items = wi_res.scalars().all()

            # Check if any items in this milestone are currently blocked
            wi_ids = [w.id for w in work_items]
            blocked_count = 0
            if wi_ids:
                dep_stmt = select(func.count()).select_from(Dependency).where(
                    Dependency.source_item_id.in_(wi_ids),
                    Dependency.status == "active",
                )
                blocked_count = await session.scalar(dep_stmt) or 0

            # Determine at_risk heuristic:
            # Milestone is at risk if: blocked items > 0 or target date is within 7 days and completion < 50%
            at_risk = False
            if blocked_count > 0:
                at_risk = True
            elif ms_resp.target_date:
                days_left = (ms_resp.target_date - datetime.now(timezone.utc).date()).days
                if days_left < 7 and ms_resp.completion_percent < 50.0:
                    at_risk = True

            timeline.append(TimelineItemResponse(
                milestone=ms_resp,
                work_items=[WorkItemResponse.model_validate(w) for w in work_items],
                blocked_count=blocked_count,
                at_risk=at_risk,
            ))

        return timeline
