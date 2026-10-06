import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.audit import AuditLog
from app.models.data_quality import DataQualityCheck
from app.models.project import DataSource, Project
from app.models.risk import RiskEvent
from app.models.work_item import Dependency, Milestone, WorkItem
from app.schemas.project import (
    DataSourceCreate,
    DataSourceResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectSummaryCounts,
    ProjectSummaryResponse,
    ProjectUpdate,
)
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.project")


class ProjectService:
    """Service handling project management CRUD, data sources, and summary aggregation."""

    @staticmethod
    async def create_project(session: AsyncSession, data: ProjectCreate) -> ProjectResponse:
        """Create a new project entity."""
        project = Project(
            name=data.name,
            description=data.description,
            project_type=data.project_type,
            status="active",
            health="green",
        )
        session.add(project)
        await session.flush()

        audit = AuditLog(
            project_id=project.id,
            event_type="project_created",
            entity_type="project",
            entity_id=project.id,
            actor="user",
            details={"name": project.name, "type": project.project_type},
        )
        session.add(audit)
        await session.commit()
        await session.refresh(project)

        logger.info("Created project", project_id=str(project.id), name=project.name)
        return ProjectResponse.model_validate(project)

    @staticmethod
    async def get_project(session: AsyncSession, project_id: uuid.UUID) -> Optional[ProjectResponse]:
        """Fetch project by ID with attached data sources."""
        stmt = (
            select(Project)
            .options(selectinload(Project.data_sources))
            .where(Project.id == project_id)
        )
        result = await session.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            return None
        return ProjectResponse.model_validate(project)

    @staticmethod
    async def list_projects(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        health: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[ProjectResponse], int]:
        """List projects with optional status/health filters and pagination."""
        query = select(Project).options(selectinload(Project.data_sources))
        count_query = select(func.count()).select_from(Project)

        if health:
            query = query.where(Project.health == health)
            count_query = count_query.where(Project.health == health)
        if status:
            query = query.where(Project.status == status)
            count_query = count_query.where(Project.status == status)

        total_res = await session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(Project.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        res = await session.execute(query)
        projects = res.scalars().all()

        return [ProjectResponse.model_validate(p) for p in projects], total

    @staticmethod
    async def update_project(
        session: AsyncSession,
        project_id: uuid.UUID,
        data: ProjectUpdate,
    ) -> Optional[ProjectResponse]:
        """Update an existing project's metadata or health."""
        stmt = select(Project).where(Project.id == project_id)
        result = await session.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            return None

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(project, key, value)

        project.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(project)

        logger.info("Updated project", project_id=str(project.id), updates=update_dict)
        return ProjectResponse.model_validate(project)

    @staticmethod
    async def delete_project(session: AsyncSession, project_id: uuid.UUID) -> bool:
        """Delete a project and cascade delete all associated entities."""
        stmt = select(Project).where(Project.id == project_id)
        result = await session.execute(stmt)
        project = result.scalar_one_or_none()
        if not project:
            return False

        await session.delete(project)
        await session.commit()
        logger.info("Deleted project", project_id=str(project_id))
        return True

    @staticmethod
    async def get_project_summary(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> Optional[ProjectSummaryResponse]:
        """Aggregate summary counts across work items, milestones, blockers, and risks."""
        project_resp = await ProjectService.get_project(session, project_id)
        if not project_resp:
            return None

        # Work items counts
        wi_total = await session.scalar(
            select(func.count()).select_from(WorkItem).where(WorkItem.project_id == project_id)
        ) or 0
        wi_open = await session.scalar(
            select(func.count()).select_from(WorkItem).where(
                WorkItem.project_id == project_id, WorkItem.status == "open"
            )
        ) or 0
        wi_wip = await session.scalar(
            select(func.count()).select_from(WorkItem).where(
                WorkItem.project_id == project_id, WorkItem.status == "in_progress"
            )
        ) or 0
        wi_done = await session.scalar(
            select(func.count()).select_from(WorkItem).where(
                WorkItem.project_id == project_id, WorkItem.status.in_(["done", "closed"])
            )
        ) or 0

        # Milestones counts
        ms_total = await session.scalar(
            select(func.count()).select_from(Milestone).where(Milestone.project_id == project_id)
        ) or 0
        ms_open = await session.scalar(
            select(func.count()).select_from(Milestone).where(
                Milestone.project_id == project_id, Milestone.status == "open"
            )
        ) or 0

        # Dependencies counts
        dep_total = await session.scalar(
            select(func.count()).select_from(Dependency).where(Dependency.project_id == project_id)
        ) or 0
        dep_active = await session.scalar(
            select(func.count()).select_from(Dependency).where(
                Dependency.project_id == project_id, Dependency.status == "active"
            )
        ) or 0

        # Risks counts
        risks_active = await session.scalar(
            select(func.count()).select_from(RiskEvent).where(
                RiskEvent.project_id == project_id, RiskEvent.status.in_(["new", "active"])
            )
        ) or 0
        risks_critical = await session.scalar(
            select(func.count()).select_from(RiskEvent).where(
                RiskEvent.project_id == project_id,
                RiskEvent.status.in_(["new", "active"]),
                RiskEvent.severity == "critical",
            )
        ) or 0

        # Latest data quality score
        latest_dq = await session.scalar(
            select(DataQualityCheck.score)
            .where(DataQualityCheck.project_id == project_id)
            .order_by(DataQualityCheck.created_at.desc())
            .limit(1)
        )
        dq_score = latest_dq if latest_dq is not None else 100.0

        # Last synced at
        last_sync = await session.scalar(
            select(func.max(DataSource.last_synced_at)).where(DataSource.project_id == project_id)
        )

        counts = ProjectSummaryCounts(
            total_work_items=wi_total,
            open_work_items=wi_open,
            in_progress_work_items=wi_wip,
            completed_work_items=wi_done,
            total_milestones=ms_total,
            open_milestones=ms_open,
            total_dependencies=dep_total,
            active_blockers=dep_active,
            active_risks_count=risks_active,
            critical_risks_count=risks_critical,
            data_quality_score=dq_score,
        )

        return ProjectSummaryResponse(
            project=project_resp,
            counts=counts,
            last_synced_at=last_sync,
        )

    @staticmethod
    async def register_data_source(
        session: AsyncSession,
        project_id: uuid.UUID,
        data: DataSourceCreate,
    ) -> Optional[DataSourceResponse]:
        """Register a new external data source for a project."""
        project = await session.get(Project, project_id)
        if not project:
            return None

        data_source = DataSource(
            project_id=project_id,
            source_type=data.source_type,
            config=data.config,
            status="connected",
        )
        session.add(data_source)
        await session.commit()
        await session.refresh(data_source)

        logger.info(
            "Registered data source",
            project_id=str(project_id),
            source_type=data_source.source_type,
            source_id=str(data_source.id),
        )
        return DataSourceResponse.model_validate(data_source)

    @staticmethod
    async def list_data_sources(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> list[DataSourceResponse]:
        """List all data sources configured for a project."""
        stmt = select(DataSource).where(DataSource.project_id == project_id).order_by(DataSource.created_at.asc())
        result = await session.execute(stmt)
        sources = result.scalars().all()
        return [DataSourceResponse.model_validate(s) for s in sources]
