import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import BudgetRecord
from app.models.data_quality import DataQualityCheck
from app.models.project import Project
from app.models.risk import RiskEvent
from app.models.snapshot import ProjectSnapshot
from app.models.work_item import Dependency, Milestone, WorkItem
from app.schemas.snapshot import ProjectSnapshotResponse
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.snapshot")


class SnapshotService:
    """Service capturing point-in-time state snapshots for historical replay and trend analysis."""

    @staticmethod
    async def capture_snapshot(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> ProjectSnapshotResponse:
        """Capture complete current project state as JSON and persist ProjectSnapshot."""
        now = datetime.now(timezone.utc)
        project = await session.get(Project, project_id)
        if not project:
            raise ValueError("Project not found")

        # Gather metrics
        wi_total = await session.scalar(select(func.count()).select_from(WorkItem).where(WorkItem.project_id == project_id)) or 0
        wi_open = await session.scalar(select(func.count()).select_from(WorkItem).where(WorkItem.project_id == project_id, WorkItem.status == "open")) or 0
        wi_wip = await session.scalar(select(func.count()).select_from(WorkItem).where(WorkItem.project_id == project_id, WorkItem.status == "in_progress")) or 0
        wi_done = await session.scalar(select(func.count()).select_from(WorkItem).where(WorkItem.project_id == project_id, WorkItem.status.in_(["done", "closed"]))) or 0

        ms_total = await session.scalar(select(func.count()).select_from(Milestone).where(Milestone.project_id == project_id)) or 0
        dep_active = await session.scalar(select(func.count()).select_from(Dependency).where(Dependency.project_id == project_id, Dependency.status == "active")) or 0
        risks_count = await session.scalar(select(func.count()).select_from(RiskEvent).where(RiskEvent.project_id == project_id, RiskEvent.status.in_(["new", "active"]))) or 0

        dq_score = await session.scalar(
            select(DataQualityCheck.score).where(DataQualityCheck.project_id == project_id).order_by(DataQualityCheck.created_at.desc()).limit(1)
        ) or 100.0

        metrics = {
            "total_work_items": wi_total,
            "open_work_items": wi_open,
            "in_progress_work_items": wi_wip,
            "completed_work_items": wi_done,
            "total_milestones": ms_total,
            "active_blockers": dep_active,
            "active_risks": risks_count,
            "data_quality_score": dq_score,
            "health": project.health,
        }

        # Serialized lightweight state
        wi_res = await session.execute(select(WorkItem.id, WorkItem.title, WorkItem.status, WorkItem.priority, WorkItem.assignee).where(WorkItem.project_id == project_id))
        items_summary = [{"id": str(r[0]), "title": r[1], "status": r[2], "priority": r[3], "assignee": r[4]} for r in wi_res.all()]

        state = {
            "project_name": project.name,
            "status": project.status,
            "health": project.health,
            "work_items": items_summary,
            "captured_at": now.isoformat(),
        }

        snapshot = ProjectSnapshot(
            project_id=project_id,
            snapshot_date=now,
            health=project.health,
            metrics_summary=metrics,
            state_json=state,
        )
        session.add(snapshot)
        await session.commit()
        await session.refresh(snapshot)

        logger.info("Captured project snapshot", project_id=str(project_id), snapshot_id=str(snapshot.id))
        return ProjectSnapshotResponse.model_validate(snapshot)

    @staticmethod
    async def list_snapshots(
        session: AsyncSession,
        project_id: uuid.UUID,
        limit: int = 30,
    ) -> list[ProjectSnapshotResponse]:
        """List historical snapshots for a project."""
        stmt = (
            select(ProjectSnapshot)
            .where(ProjectSnapshot.project_id == project_id)
            .order_by(ProjectSnapshot.snapshot_date.desc())
            .limit(limit)
        )
        res = await session.execute(stmt)
        snaps = res.scalars().all()
        return [ProjectSnapshotResponse.model_validate(s) for s in snaps]
