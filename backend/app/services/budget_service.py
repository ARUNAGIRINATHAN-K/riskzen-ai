import uuid
from typing import Optional
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.csv_budget import CSVBudgetConnector
from app.models.budget import BudgetRecord
from app.models.project import Project
from app.schemas.budget import BudgetRecordResponse, BudgetSummaryResponse
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.budget")


class BudgetService:
    """Service handling CSV budget upload, parsing, validation, and summary reporting."""

    @staticmethod
    async def ingest_csv_budget(
        session: AsyncSession,
        project_id: uuid.UUID,
        csv_content: str,
        filename: str = "budget.csv",
    ) -> list[BudgetRecordResponse]:
        """Parse CSV budget data and replace existing records for the same periods."""
        project = await session.get(Project, project_id)
        if not project:
            raise ValueError("Project not found")

        connector = CSVBudgetConnector({"filename": filename})
        parsed_records = connector.parse_csv_content(csv_content)

        # Collect periods in the uploaded batch
        periods_in_batch = set(r["period"] for r in parsed_records)

        # Delete previous records for these periods (replace logic)
        delete_stmt = delete(BudgetRecord).where(
            BudgetRecord.project_id == project_id,
            BudgetRecord.period.in_(periods_in_batch),
        )
        await session.execute(delete_stmt)

        # Insert new records
        created_entities = []
        for r in parsed_records:
            record = BudgetRecord(
                project_id=project_id,
                period=r["period"],
                category=r["category"],
                planned_amount=r["planned_amount"],
                actual_amount=r["actual_amount"],
                variance=r["variance"],
                currency=r["currency"],
                source_filename=filename,
            )
            session.add(record)
            created_entities.append(record)

        await session.commit()

        for rec in created_entities:
            await session.refresh(rec)

        logger.info(
            "Ingested CSV budget records",
            project_id=str(project_id),
            records_count=len(created_entities),
            periods=list(periods_in_batch),
        )

        return [BudgetRecordResponse.model_validate(r) for r in created_entities]

    @staticmethod
    async def list_budget_records(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> list[BudgetRecordResponse]:
        """List all budget records for a project."""
        stmt = (
            select(BudgetRecord)
            .where(BudgetRecord.project_id == project_id)
            .order_by(BudgetRecord.period.asc(), BudgetRecord.category.asc())
        )
        res = await session.execute(stmt)
        records = res.scalars().all()
        return [BudgetRecordResponse.model_validate(r) for r in records]

    @staticmethod
    async def get_budget_summary(
        session: AsyncSession,
        project_id: uuid.UUID,
    ) -> Optional[BudgetSummaryResponse]:
        """Compute aggregated budget totals and variance across all ingested periods."""
        records = await BudgetService.list_budget_records(session, project_id)
        if not records:
            return None

        total_planned = sum(r.planned_amount for r in records)
        total_actual = sum(r.actual_amount for r in records)
        total_variance = round(total_actual - total_planned, 2)
        periods = set(r.period for r in records)
        categories = sorted(list(set(r.category for r in records)))
        currency = records[0].currency if records else "USD"

        return BudgetSummaryResponse(
            total_planned=round(total_planned, 2),
            total_actual=round(total_actual, 2),
            total_variance=total_variance,
            currency=currency,
            periods_count=len(periods),
            categories=categories,
            records=records,
        )
