import uuid
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select

from app.config import settings
from app.database import async_session_factory
from app.models.project import Project
from app.services.snapshot_service import SnapshotService
from app.services.sync_service import SyncService
from app.utils.logging import get_logger

logger = get_logger("riskzen.scheduler")

scheduler = AsyncIOScheduler()


async def sync_active_projects():
    """Periodic job syncing data sources for all active projects."""
    logger.info("Starting scheduled background sync job")
    async with async_session_factory() as session:
        stmt = select(Project.id).where(Project.status == "active")
        res = await session.execute(stmt)
        project_ids = res.scalars().all()

        for pid in project_ids:
            try:
                await SyncService.execute_sync(session, project_id=pid)
            except Exception as exc:
                logger.error("Scheduled sync failed for project", project_id=str(pid), error=str(exc))


async def capture_daily_snapshots():
    """Periodic job capturing point-in-time snapshots for trend analysis."""
    logger.info("Starting scheduled daily snapshot job")
    async with async_session_factory() as session:
        stmt = select(Project.id).where(Project.status == "active")
        res = await session.execute(stmt)
        project_ids = res.scalars().all()

        for pid in project_ids:
            try:
                await SnapshotService.capture_snapshot(session, project_id=pid)
            except Exception as exc:
                logger.error("Scheduled snapshot failed for project", project_id=str(pid), error=str(exc))


def start_scheduler():
    """Register cron/interval jobs and start the background scheduler."""
    sync_interval = settings.SYNC_INTERVAL_MINUTES
    scheduler.add_job(
        sync_active_projects,
        "interval",
        minutes=sync_interval,
        id="sync_active_projects_job",
        replace_existing=True,
    )
    scheduler.add_job(
        capture_daily_snapshots,
        "cron",
        hour=0,
        minute=0,
        id="daily_snapshot_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started successfully", sync_interval_minutes=sync_interval)


def shutdown_scheduler():
    """Shut down the background scheduler cleanly."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
