import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.csv_budget import CSVBudgetConnector
from app.connectors.github import GitHubConnector
from app.models.audit import AuditLog
from app.models.budget import BudgetRecord
from app.models.project import DataSource, Project
from app.models.sync import SyncJob
from app.models.work_item import Dependency, Milestone, WorkItem
from app.schemas.sync import SyncJobResponse
from app.services.data_quality_service import DataQualityService
from app.services.dependency_service import DependencyService
from app.services.milestone_service import MilestoneService
from app.services.work_item_service import WorkItemService
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.sync")


class SyncService:
    """Service orchestrating external data source ingestion, DB normalization, and sync history."""

    @staticmethod
    async def execute_sync(
        session: AsyncSession,
        project_id: uuid.UUID,
        data_source_id: Optional[uuid.UUID] = None,
        force_full: bool = False,
    ) -> list[SyncJobResponse]:
        """Trigger sync execution for one or all data sources attached to a project."""
        project = await session.get(Project, project_id)
        if not project:
            raise ValueError(f"Project '{project_id}' not found.")

        # Find data sources to sync
        stmt = select(DataSource).where(DataSource.project_id == project_id)
        if data_source_id:
            stmt = stmt.where(DataSource.id == data_source_id)

        res = await session.execute(stmt)
        data_sources = res.scalars().all()

        if not data_sources:
            return []

        job_responses: list[SyncJobResponse] = []

        for ds in data_sources:
            job = SyncJob(
                project_id=project_id,
                data_source_id=ds.id,
                status="running",
                started_at=datetime.now(timezone.utc),
                items_synced=0,
                details={},
            )
            session.add(job)
            await session.commit()
            await session.refresh(job)

            try:
                ds.status = "syncing"
                await session.commit()

                # Determine since timestamp for incremental sync
                since_time = None if force_full else ds.last_synced_at

                if ds.source_type == "github":
                    connector = GitHubConnector(ds.config)
                    sync_result = await connector.sync(since=since_time)

                    if sync_result.success:
                        details = sync_result.details or {}

                        # 1. Upsert Milestones
                        ext_to_db_milestone: dict[str, uuid.UUID] = {}
                        for m_data in details.get("milestones", []):
                            ms_obj, _ = await MilestoneService.upsert_milestone(session, project_id, m_data)
                            if ms_obj.external_id:
                                ext_to_db_milestone[ms_obj.external_id] = ms_obj.id

                        # 2. Upsert Work Items
                        ext_to_db_workitem: dict[str, uuid.UUID] = {}
                        for wi_data in details.get("work_items", []):
                            # Map milestone_external_id to database milestone UUID
                            ms_ext = wi_data.get("milestone_external_id")
                            if ms_ext and ms_ext in ext_to_db_milestone:
                                wi_data["milestone_id"] = ext_to_db_milestone[ms_ext]

                            wi_obj, _ = await WorkItemService.upsert_work_item(session, project_id, wi_data)
                            if wi_obj.external_id:
                                ext_to_db_workitem[wi_obj.external_id] = wi_obj.id

                        # 3. Upsert Dependencies
                        deps_created = 0
                        for dep_data in details.get("dependencies", []):
                            src_ext = dep_data.get("source_external_id")
                            tgt_ext = dep_data.get("target_external_id")
                            if src_ext in ext_to_db_workitem and tgt_ext in ext_to_db_workitem:
                                src_id = ext_to_db_workitem[src_ext]
                                tgt_id = ext_to_db_workitem[tgt_ext]
                                _, was_created = await DependencyService.upsert_dependency(
                                    session, project_id, src_id, tgt_id, dep_data.get("dependency_type", "blocks")
                                )
                                if was_created:
                                    deps_created += 1

                        job.status = "completed"
                        job.items_synced = sync_result.items_created + sync_result.milestones_synced
                        job.details = {
                            "work_items_synced": sync_result.items_created,
                            "milestones_synced": sync_result.milestones_synced,
                            "dependencies_detected": len(details.get("dependencies", [])),
                        }
                        ds.status = "connected"
                        ds.last_synced_at = datetime.now(timezone.utc)
                    else:
                        job.status = "failed"
                        job.error_message = "; ".join(sync_result.errors)
                        ds.status = "error"

                elif ds.source_type == "csv_budget":
                    connector = CSVBudgetConnector(ds.config)
                    sync_result = await connector.sync(since=since_time)
                    if sync_result.success:
                        budget_records = sync_result.details.get("budget_records", [])
                        for r in budget_records:
                            rec = BudgetRecord(
                                project_id=project_id,
                                period=r["period"],
                                category=r["category"],
                                planned_amount=r["planned_amount"],
                                actual_amount=r["actual_amount"],
                                variance=r["variance"],
                                currency=r["currency"],
                                source_filename=r.get("source_filename", "budget.csv"),
                            )
                            session.add(rec)
                        job.status = "completed"
                        job.items_synced = len(budget_records)
                        ds.status = "connected"
                        ds.last_synced_at = datetime.now(timezone.utc)
                    else:
                        job.status = "failed"
                        job.error_message = "; ".join(sync_result.errors)
                        ds.status = "error"

                job.completed_at = datetime.now(timezone.utc)
                await session.commit()

                # Trigger data-quality re-evaluation after sync
                try:
                    await DataQualityService.evaluate_data_quality(session, project_id)
                except Exception as dq_err:
                    logger.warn("Data quality evaluation failed post-sync", error=str(dq_err))

                # Log audit record
                audit = AuditLog(
                    project_id=project_id,
                    event_type="sync_completed" if job.status == "completed" else "sync_failed",
                    entity_type="data_source",
                    entity_id=ds.id,
                    actor="system",
                    details={
                        "source_type": ds.source_type,
                        "status": job.status,
                        "items_synced": job.items_synced,
                        "error": job.error_message,
                    },
                )
                session.add(audit)
                await session.commit()
                await session.refresh(job)

                logger.info(
                    "Sync execution completed",
                    project_id=str(project_id),
                    source_id=str(ds.id),
                    status=job.status,
                    synced=job.items_synced,
                )

            except Exception as exc:
                logger.error("Sync execution crashed", error=str(exc))
                job.status = "failed"
                job.error_message = str(exc)
                job.completed_at = datetime.now(timezone.utc)
                ds.status = "error"
                await session.commit()
                await session.refresh(job)

            job_responses.append(SyncJobResponse.model_validate(job))

        return job_responses

    @staticmethod
    async def get_sync_history(
        session: AsyncSession,
        project_id: uuid.UUID,
        limit: int = 20,
    ) -> list[SyncJobResponse]:
        """Fetch list of recent sync jobs."""
        stmt = (
            select(SyncJob)
            .where(SyncJob.project_id == project_id)
            .order_by(SyncJob.started_at.desc())
            .limit(limit)
        )
        res = await session.execute(stmt)
        jobs = res.scalars().all()
        return [SyncJobResponse.model_validate(j) for j in jobs]
