import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.work_item import Dependency, WorkItem
from app.schemas.work_item import DependencyCreate, DependencyResponse
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.dependency")


class DependencyService:
    """Service handling dependency tracking and blocker graph resolution."""

    @staticmethod
    async def create_dependency(
        session: AsyncSession,
        project_id: uuid.UUID,
        data: DependencyCreate,
    ) -> DependencyResponse:
        """Create a new dependency relation between two work items."""
        dep = Dependency(
            project_id=project_id,
            source_item_id=data.source_item_id,
            target_item_id=data.target_item_id,
            dependency_type=data.dependency_type,
            status="active",
        )
        session.add(dep)
        await session.commit()
        await session.refresh(dep)
        return await DependencyService._to_response(session, dep)

    @staticmethod
    async def upsert_dependency(
        session: AsyncSession,
        project_id: uuid.UUID,
        source_item_id: uuid.UUID,
        target_item_id: uuid.UUID,
        dependency_type: str = "blocks",
    ) -> tuple[Dependency, bool]:
        """Upsert a dependency avoiding duplicates."""
        stmt = select(Dependency).where(
            Dependency.project_id == project_id,
            Dependency.source_item_id == source_item_id,
            Dependency.target_item_id == target_item_id,
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            existing.dependency_type = dependency_type
            return existing, False

        dep = Dependency(
            project_id=project_id,
            source_item_id=source_item_id,
            target_item_id=target_item_id,
            dependency_type=dependency_type,
            status="active",
        )
        session.add(dep)
        await session.flush()
        return dep, True

    @staticmethod
    async def list_dependencies(
        session: AsyncSession,
        project_id: uuid.UUID,
        status: Optional[str] = None,
    ) -> list[DependencyResponse]:
        """List dependencies with work item titles."""
        stmt = (
            select(Dependency)
            .options(
                selectinload(Dependency.source_item),
                selectinload(Dependency.target_item),
            )
            .where(Dependency.project_id == project_id)
            .order_by(Dependency.detected_at.desc())
        )
        if status:
            stmt = stmt.where(Dependency.status == status)

        result = await session.execute(stmt)
        deps = result.scalars().all()

        responses = []
        for d in deps:
            resp = DependencyResponse(
                id=d.id,
                project_id=d.project_id,
                source_item_id=d.source_item_id,
                target_item_id=d.target_item_id,
                dependency_type=d.dependency_type,
                status=d.status,
                detected_at=d.detected_at,
                resolved_at=d.resolved_at,
                source_item_title=d.source_item.title if d.source_item else None,
                target_item_title=d.target_item.title if d.target_item else None,
            )
            responses.append(resp)
        return responses

    @staticmethod
    async def resolve_dependency(
        session: AsyncSession,
        project_id: uuid.UUID,
        dependency_id: uuid.UUID,
    ) -> Optional[DependencyResponse]:
        """Mark a dependency as resolved."""
        stmt = select(Dependency).where(
            Dependency.id == dependency_id,
            Dependency.project_id == project_id,
        )
        res = await session.execute(stmt)
        dep = res.scalar_one_or_none()
        if not dep:
            return None

        dep.status = "resolved"
        dep.resolved_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(dep)
        return await DependencyService._to_response(session, dep)

    @staticmethod
    async def _to_response(session: AsyncSession, dep: Dependency) -> DependencyResponse:
        source_title = None
        target_title = None
        source_item = await session.get(WorkItem, dep.source_item_id)
        if source_item:
            source_title = source_item.title
        target_item = await session.get(WorkItem, dep.target_item_id)
        if target_item:
            target_title = target_item.title

        return DependencyResponse(
            id=dep.id,
            project_id=dep.project_id,
            source_item_id=dep.source_item_id,
            target_item_id=dep.target_item_id,
            dependency_type=dep.dependency_type,
            status=dep.status,
            detected_at=dep.detected_at,
            resolved_at=dep.resolved_at,
            source_item_title=source_title,
            target_item_title=target_title,
        )
