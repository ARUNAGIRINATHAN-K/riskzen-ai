import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import DataSource, Project
from app.seed import SEED_WORK_ITEMS, TEAM_MEMBERS, seed_database


@pytest.mark.asyncio
async def test_seed_database_execution(db_session: AsyncSession):
    """Test seed_database creates project and data sources properly."""
    project = await seed_database(db_session)

    assert project is not None
    assert project.name == "NovaPay — Mobile Checkout Revamp"
    assert project.health == "yellow"
    assert project.status == "active"

    # Verify query
    stmt = select(Project).where(Project.id == project.id)
    result = await db_session.execute(stmt)
    saved_project = result.scalar_one_or_none()

    assert saved_project is not None
    assert len(saved_project.data_sources) == 2
    source_types = [ds.source_type for ds in saved_project.data_sources]
    assert "github" in source_types
    assert "csv_budget" in source_types


def test_seed_risk_patterns_integrity():
    """Verify seed data definitions contain the required risk scenarios."""
    # 1. Check Team Size is 7
    assert len(TEAM_MEMBERS) == 7

    # 2. Check for blocked dependency scenario
    blocked_items = [item for item in SEED_WORK_ITEMS if "blocked_by" in item]
    assert len(blocked_items) >= 2
    # Verify cascading block: NOVA-105 blocked by NOVA-103, which is blocked by NOVA-102
    item_105 = next(i for i in SEED_WORK_ITEMS if i["external_id"] == "NOVA-105")
    item_103 = next(i for i in SEED_WORK_ITEMS if i["external_id"] == "NOVA-103")
    assert item_105["blocked_by"] == "NOVA-103"
    assert item_103["blocked_by"] == "NOVA-102"

    # 3. Check for capacity bottleneck on Alex Chen
    alex_tasks = [i for i in SEED_WORK_ITEMS if i.get("assignee") == "Alex Chen"]
    assert len(alex_tasks) >= 3

    # 4. Check for unestimated scope creep
    scope_creep_items = [i for i in SEED_WORK_ITEMS if "scope-creep" in i["labels"]]
    assert len(scope_creep_items) >= 2

    # 5. Check for decision latency / stalled PR
    stalled_decisions = [i for i in SEED_WORK_ITEMS if "decision-latency" in i["labels"]]
    assert len(stalled_decisions) >= 1
