import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import BudgetRecord
from app.models.data_quality import DataQualityCheck
from app.models.project import DataSource, Project
from app.models.snapshot import ProjectSnapshot
from app.models.team import Team, TeamMember
from app.models.work_item import Dependency, Milestone, WorkItem
from app.seed import SEED_WORK_ITEMS, TEAM_MEMBERS, seed_database


@pytest.mark.asyncio
async def test_seed_database_execution(db_session: AsyncSession):
    """Test seed_database creates project and all related entities properly."""
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

    # Check data sources
    assert len(saved_project.data_sources) == 2

    # Check work items
    wi_count = await db_session.scalar(select(func.count()).select_from(WorkItem).where(WorkItem.project_id == project.id))
    assert wi_count == len(SEED_WORK_ITEMS)

    # Check milestones
    ms_count = await db_session.scalar(select(func.count()).select_from(Milestone).where(Milestone.project_id == project.id))
    assert ms_count == 3

    # Check dependencies
    dep_count = await db_session.scalar(select(func.count()).select_from(Dependency).where(Dependency.project_id == project.id))
    assert dep_count == 2

    # Check teams & members
    member_count = await db_session.scalar(select(func.count()).select_from(TeamMember))
    assert member_count == len(TEAM_MEMBERS)

    # Check budget records
    budget_count = await db_session.scalar(select(func.count()).select_from(BudgetRecord).where(BudgetRecord.project_id == project.id))
    assert budget_count == 4

    # Check data quality check generated
    dq_count = await db_session.scalar(select(func.count()).select_from(DataQualityCheck).where(DataQualityCheck.project_id == project.id))
    assert dq_count == 5

    # Check snapshot captured
    snap_count = await db_session.scalar(select(func.count()).select_from(ProjectSnapshot).where(ProjectSnapshot.project_id == project.id))
    assert snap_count == 1


def test_seed_risk_patterns_integrity():
    """Verify seed data definitions contain the required risk scenarios."""
    assert len(TEAM_MEMBERS) == 7

    # Blocked dependency scenario
    blocked_items = [item for item in SEED_WORK_ITEMS if "blocked_by" in item]
    assert len(blocked_items) >= 2
    item_105 = next(i for i in SEED_WORK_ITEMS if i["external_id"] == "NOVA-105")
    item_103 = next(i for i in SEED_WORK_ITEMS if i["external_id"] == "NOVA-103")
    assert item_105["blocked_by"] == "NOVA-103"
    assert item_103["blocked_by"] == "NOVA-102"

    # Capacity bottleneck on Alex Chen
    alex_tasks = [i for i in SEED_WORK_ITEMS if i.get("assignee") == "Alex Chen"]
    assert len(alex_tasks) >= 3

    # Unestimated scope creep
    scope_creep_items = [i for i in SEED_WORK_ITEMS if "scope-creep" in i["labels"]]
    assert len(scope_creep_items) >= 2

    # Decision latency / stalled PR
    stalled_decisions = [i for i in SEED_WORK_ITEMS if "decision-latency" in i["labels"]]
    assert len(stalled_decisions) >= 1
