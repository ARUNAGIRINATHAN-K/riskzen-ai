import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.work_item import WorkItem
from app.schemas.work_item import WorkItemCreate, WorkItemResponse, WorkItemUpdate
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.work_item")


class WorkItemService:
    """Service handling normalized work item CRUD and filtering."""

    @staticmethod
    async def create_work_item(
        session: AsyncSession,
        project_id: uuid.UUID,
        data: WorkItemCreate,
    ) -> WorkItemResponse:
        """Create a new work item."""
        item = WorkItem(
            project_id=project_id,
            milestone_id=data.milestone_id,
            external_id=data.external_id,
            source_type=data.source_type,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            item_type=data.item_type,
            assignee=data.assignee,
            labels=data.labels,
            due_date=data.due_date,
            metadata_json=data.metadata_json,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return WorkItemResponse.model_validate(item)

    @staticmethod
    async def upsert_work_item(
        session: AsyncSession,
        project_id: uuid.UUID,
        item_data: dict,
    ) -> tuple[WorkItem, bool]:
        """Upsert a work item matching external_id and source_type for deduplication."""
        ext_id = item_data.get("external_id")
        existing = None
        if ext_id:
            stmt = select(WorkItem).where(
                WorkItem.project_id == project_id,
                WorkItem.external_id == ext_id,
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

        is_created = False
        if existing:
            # Update existing
            for key in ["title", "description", "status", "priority", "item_type", "assignee", "labels", "due_date", "completed_at", "cycle_time_hours", "milestone_id"]:
                if key in item_data and item_data[key] is not None:
                    setattr(existing, key, item_data[key])
            if "metadata_json" in item_data:
                existing.metadata_json = {**existing.metadata_json, **item_data["metadata_json"]}
            existing.updated_at = datetime.now(timezone.utc)
            item = existing
        else:
            # Create new
            item = WorkItem(
                project_id=project_id,
                milestone_id=item_data.get("milestone_id"),
                external_id=ext_id,
                source_type=item_data.get("source_type", "github"),
                title=item_data["title"],
                description=item_data.get("description"),
                status=item_data.get("status", "open"),
                priority=item_data.get("priority", "medium"),
                item_type=item_data.get("item_type", "task"),
                assignee=item_data.get("assignee"),
                labels=item_data.get("labels", []),
                due_date=item_data.get("due_date"),
                completed_at=item_data.get("completed_at"),
                cycle_time_hours=item_data.get("cycle_time_hours"),
                metadata_json=item_data.get("metadata_json", {}),
            )
            session.add(item)
            is_created = True

        await session.flush()
        return item, is_created

    @staticmethod
    async def get_work_item(
        session: AsyncSession,
        project_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> Optional[WorkItemResponse]:
        """Fetch a single work item."""
        stmt = select(WorkItem).where(WorkItem.id == item_id, WorkItem.project_id == project_id)
        res = await session.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            return None
        return WorkItemResponse.model_validate(item)

    @staticmethod
    async def list_work_items(
        session: AsyncSession,
        project_id: uuid.UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        item_type: Optional[str] = None,
        milestone_id: Optional[uuid.UUID] = None,
        page: int = 1,
        per_page: int = 50,
    ) -> tuple[list[WorkItemResponse], int]:
        """List work items matching query criteria with pagination."""
        query = select(WorkItem).where(WorkItem.project_id == project_id)
        count_query = select(func.count()).select_from(WorkItem).where(WorkItem.project_id == project_id)

        if status:
            query = query.where(WorkItem.status == status)
            count_query = count_query.where(WorkItem.status == status)
        if priority:
            query = query.where(WorkItem.priority == priority)
            count_query = count_query.where(WorkItem.priority == priority)
        if assignee:
            query = query.where(WorkItem.assignee == assignee)
            count_query = count_query.where(WorkItem.assignee == assignee)
        if item_type:
            query = query.where(WorkItem.item_type == item_type)
            count_query = count_query.where(WorkItem.item_type == item_type)
        if milestone_id:
            query = query.where(WorkItem.milestone_id == milestone_id)
            count_query = count_query.where(WorkItem.milestone_id == milestone_id)

        total_res = await session.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(WorkItem.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        res = await session.execute(query)
        items = res.scalars().all()

        return [WorkItemResponse.model_validate(i) for i in items], total

    @staticmethod
    async def update_work_item(
        session: AsyncSession,
        project_id: uuid.UUID,
        item_id: uuid.UUID,
        data: WorkItemUpdate,
    ) -> Optional[WorkItemResponse]:
        """Update a work item."""
        stmt = select(WorkItem).where(WorkItem.id == item_id, WorkItem.project_id == project_id)
        res = await session.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            return None

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(item, key, value)

        item.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(item)
        return WorkItemResponse.model_validate(item)
