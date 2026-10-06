import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import BudgetRecord
from app.models.data_quality import DataQualityCheck
from app.models.project import Project
from app.models.work_item import Dependency, Milestone, WorkItem
from app.schemas.data_quality import DataQualityCheckResponse, DataQualityReportResponse
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.data_quality")


class DataQualityService:
    """Service evaluating and scoring data quality across work items, milestones, dependencies, and budget."""

    @staticmethod
    async def evaluate_data_quality(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> DataQualityReportResponse:
        """Run all data-quality rules, calculate composite score, and persist results."""
        now = datetime.now(timezone.utc)
        project = await session.get(Project, project_id)
        if not project:
            raise ValueError("Project not found")

        checks: list[DataQualityCheck] = []

        # ── Check 1: Missing Due Dates on Open Work Items ──
        total_open_items_stmt = select(func.count()).select_from(WorkItem).where(
            WorkItem.project_id == project_id,
            WorkItem.status.in_(["open", "in_progress"]),
        )
        total_open_items = await session.scalar(total_open_items_stmt) or 0

        missing_due_stmt = select(func.count()).select_from(WorkItem).where(
            WorkItem.project_id == project_id,
            WorkItem.status.in_(["open", "in_progress"]),
            WorkItem.due_date.is_(None),
        )
        missing_due_count = await session.scalar(missing_due_stmt) or 0

        if total_open_items == 0:
            c1_score = 100.0
            c1_status = "pass"
        else:
            missing_pct = (missing_due_count / total_open_items) * 100.0
            c1_score = max(0.0, 100.0 - missing_pct)
            c1_status = "pass" if missing_pct < 20.0 else ("warn" if missing_pct < 50.0 else "fail")

        c1 = DataQualityCheck(
            project_id=project_id,
            check_type="missing_due_dates",
            status=c1_status,
            score=round(c1_score, 1),
            details={
                "total_open_items": total_open_items,
                "missing_due_count": missing_due_count,
                "missing_percent": round((missing_due_count / total_open_items * 100.0) if total_open_items else 0, 1),
            },
            created_at=now,
        )
        checks.append(c1)

        # ── Check 2: Stale Work Items (no update > 14 days) ──
        stale_threshold = now - timedelta(days=14)
        stale_items_stmt = select(func.count()).select_from(WorkItem).where(
            WorkItem.project_id == project_id,
            WorkItem.status.in_(["open", "in_progress"]),
            WorkItem.updated_at < stale_threshold,
        )
        stale_count = await session.scalar(stale_items_stmt) or 0

        if total_open_items == 0:
            c2_score = 100.0
            c2_status = "pass"
        else:
            stale_pct = (stale_count / total_open_items) * 100.0
            c2_score = max(0.0, 100.0 - (stale_pct * 1.5))
            c2_status = "pass" if stale_pct < 15.0 else ("warn" if stale_pct < 35.0 else "fail")

        c2 = DataQualityCheck(
            project_id=project_id,
            check_type="stale_items",
            status=c2_status,
            score=round(c2_score, 1),
            details={
                "total_open_items": total_open_items,
                "stale_items_count": stale_count,
                "stale_percent": round((stale_count / total_open_items * 100.0) if total_open_items else 0, 1),
                "threshold_days": 14,
            },
            created_at=now,
        )
        checks.append(c2)

        # ── Check 3: Milestones Missing Target Dates ──
        total_ms_stmt = select(func.count()).select_from(Milestone).where(
            Milestone.project_id == project_id,
            Milestone.status == "open",
        )
        total_ms = await session.scalar(total_ms_stmt) or 0

        missing_target_stmt = select(func.count()).select_from(Milestone).where(
            Milestone.project_id == project_id,
            Milestone.status == "open",
            Milestone.target_date.is_(None),
        )
        missing_target_count = await session.scalar(missing_target_stmt) or 0

        if total_ms == 0:
            c3_score = 100.0
            c3_status = "pass"
        else:
            ms_missing_pct = (missing_target_count / total_ms) * 100.0
            c3_score = max(0.0, 100.0 - ms_missing_pct)
            c3_status = "pass" if missing_target_count == 0 else ("warn" if missing_target_count == 1 else "fail")

        c3 = DataQualityCheck(
            project_id=project_id,
            check_type="missing_target_dates",
            status=c3_status,
            score=round(c3_score, 1),
            details={
                "total_open_milestones": total_ms,
                "missing_target_count": missing_target_count,
            },
            created_at=now,
        )
        checks.append(c3)

        # ── Check 4: Unresolved Dependencies (Blockers) ──
        total_deps_stmt = select(func.count()).select_from(Dependency).where(
            Dependency.project_id == project_id,
        )
        total_deps = await session.scalar(total_deps_stmt) or 0

        # Check if blocker item is already closed but dependency is still active
        mismatched_deps_stmt = (
            select(func.count())
            .select_from(Dependency)
            .join(WorkItem, Dependency.target_item_id == WorkItem.id)
            .where(
                Dependency.project_id == project_id,
                Dependency.status == "active",
                WorkItem.status.in_(["done", "closed"]),
            )
        )
        mismatched_deps_count = await session.scalar(mismatched_deps_stmt) or 0

        c4_score = 100.0 if total_deps == 0 else max(0.0, 100.0 - (mismatched_deps_count * 20.0))
        c4_status = "pass" if mismatched_deps_count == 0 else ("warn" if mismatched_deps_count <= 2 else "fail")

        c4 = DataQualityCheck(
            project_id=project_id,
            check_type="unresolved_deps",
            status=c4_status,
            score=round(c4_score, 1),
            details={
                "total_dependencies": total_deps,
                "mismatched_completed_blockers": mismatched_deps_count,
            },
            created_at=now,
        )
        checks.append(c4)

        # ── Check 5: Budget Coverage ──
        budget_records_count = await session.scalar(
            select(func.count()).select_from(BudgetRecord).where(BudgetRecord.project_id == project_id)
        ) or 0

        c5_score = 100.0 if budget_records_count > 0 else 70.0  # Budget is optional but rewarded
        c5_status = "pass" if budget_records_count > 0 else "warn"

        c5 = DataQualityCheck(
            project_id=project_id,
            check_type="budget_coverage",
            status=c5_status,
            score=c5_score,
            details={
                "budget_records_count": budget_records_count,
                "has_financial_data": budget_records_count > 0,
            },
            created_at=now,
        )
        checks.append(c5)

        # ── Calculate Overall Score (Weighted) ──
        # Weights: Missing due dates (25%), Stale items (25%), Milestone dates (25%), Dependencies (15%), Budget (10%)
        weights = [0.25, 0.25, 0.25, 0.15, 0.10]
        overall_score = sum(c.score * w for c, w in zip(checks, weights))
        overall_score = round(overall_score, 1)

        # Persist all checks
        session.add_all(checks)
        await session.commit()

        for c in checks:
            await session.refresh(c)

        status_overall = "healthy" if overall_score >= 80.0 else ("needs_attention" if overall_score >= 50.0 else "poor")
        passed = sum(1 for c in checks if c.status == "pass")
        warned = sum(1 for c in checks if c.status == "warn")
        failed = sum(1 for c in checks if c.status == "fail")

        return DataQualityReportResponse(
            project_id=project_id,
            overall_score=overall_score,
            status=status_overall,
            checks_passed=passed,
            checks_warned=warned,
            checks_failed=failed,
            evaluated_at=now,
            checks=[DataQualityCheckResponse.model_validate(c) for c in checks],
        )

    @staticmethod
    async def get_data_quality_report(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> Optional[DataQualityReportResponse]:
        """Fetch the most recent data-quality evaluation or trigger a fresh one."""
        stmt = (
            select(DataQualityCheck)
            .where(DataQualityCheck.project_id == project_id)
            .order_by(DataQualityCheck.created_at.desc())
            .limit(5)
        )
        res = await session.execute(stmt)
        checks = res.scalars().all()

        if not checks:
            return await DataQualityService.evaluate_data_quality(session, project_id)

        # Calculate composite score from latest batch
        weights = [0.25, 0.25, 0.25, 0.15, 0.10]
        overall_score = round(sum(c.score * w for c, w in zip(checks[:5], weights[:len(checks)])), 1)
        status_overall = "healthy" if overall_score >= 80.0 else ("needs_attention" if overall_score >= 50.0 else "poor")
        passed = sum(1 for c in checks if c.status == "pass")
        warned = sum(1 for c in checks if c.status == "warn")
        failed = sum(1 for c in checks if c.status == "fail")

        return DataQualityReportResponse(
            project_id=project_id,
            overall_score=overall_score,
            status=status_overall,
            checks_passed=passed,
            checks_warned=warned,
            checks_failed=failed,
            evaluated_at=checks[0].created_at,
            checks=[DataQualityCheckResponse.model_validate(c) for c in checks],
        )
