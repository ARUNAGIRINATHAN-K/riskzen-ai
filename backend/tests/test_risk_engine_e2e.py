"""End-to-end tests for deterministic risk engine performance and false-positive resilience."""
import time
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.dependency import Dependency
from app.models.milestone import Milestone
from app.models.project import Project, ProjectMember
from app.models.work_item import WorkItem
from app.services.risk_engine_service import RiskEngineService


@pytest.mark.asyncio
async def test_clean_project_zero_false_positives(db_session: AsyncSession):
    """A completely healthy on-time project should produce zero high/critical risk events."""
    now = datetime.now(timezone.utc)
    proj = Project(
        id=uuid.uuid4(),
        name="Healthy Clean Project",
        key="HCP",
        status="active",
        settings={"planned_budget": 100000.0, "actual_spend": 20000.0},
    )
    db_session.add(proj)
    await db_session.flush()

    # Add 5 members
    members = [
        ProjectMember(id=uuid.uuid4(), project_id=proj.id, user_id=uuid.uuid4(), role="Developer")
        for _ in range(5)
    ]
    db_session.add_all(members)

    # Add on-track milestone
    ms = Milestone(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="Sprint Clean",
        start_date=now - timedelta(days=5),
        due_date=now + timedelta(days=20),
        status="open",
    )
    db_session.add(ms)
    await db_session.flush()

    # Add evenly distributed on-track items with story points
    items = []
    for i in range(10):
        items.append(
            WorkItem(
                id=uuid.uuid4(),
                project_id=proj.id,
                milestone_id=ms.id,
                title=f"Healthy Feature {i}",
                status="in_progress" if i < 3 else "open",
                due_date=now + timedelta(days=15),
                priority="medium",
                story_points=3.0,
                assignee_id=members[i % len(members)].user_id,
                created_at=now - timedelta(days=6),
            )
        )
    db_session.add_all(items)
    await db_session.commit()

    # Evaluate
    res = await RiskEngineService.evaluate_project(db_session, proj.id)
    assert res.overall_severity.value in ("low", "medium")
    assert res.total_signals <= 1  # Zero false positives on critical/high items


@pytest.mark.asyncio
async def test_high_risk_project_detection_and_performance(db_session: AsyncSession):
    """A project with multi-category anomalies triggers detection across categories in < 500ms."""
    now = datetime.now(timezone.utc)
    proj = Project(
        id=uuid.uuid4(),
        name="Distressed Project",
        key="DIST",
        status="active",
        settings={"planned_budget": 50000.0, "actual_spend": 85000.0},
    )
    db_session.add(proj)
    await db_session.flush()

    # Overdue Milestone
    ms = Milestone(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="Overdue Milestone",
        start_date=now - timedelta(days=30),
        due_date=now - timedelta(days=5),
        status="open",
    )
    db_session.add(ms)
    await db_session.flush()

    # 1. Schedule & Capacity: Multiple overdue tasks concentrated on one person
    single_owner = uuid.uuid4()
    items = []
    for i in range(6):
        items.append(
            WorkItem(
                id=uuid.uuid4(),
                project_id=proj.id,
                milestone_id=ms.id,
                title=f"Late Core Task {i}",
                status="in_progress",
                due_date=now - timedelta(days=10),
                priority="critical",
                assignee_id=single_owner,
                story_points=5.0,
                created_at=now - timedelta(days=25),
            )
        )

    # 2. Quality: Open critical bug
    bug = WorkItem(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="Production Data Corruption",
        item_type="bug",
        priority="critical",
        status="open",
        created_at=now - timedelta(days=15),
    )
    items.append(bug)

    # 3. Decision: Long stalled blocker
    blocker = WorkItem(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="Blocked on External API Credentials",
        status="blocked",
        created_at=now - timedelta(days=20),
        updated_at=now - timedelta(days=12),
    )
    items.append(blocker)

    db_session.add_all(items)
    await db_session.flush()

    # 4. Dependency: Blocked dependency relationship
    dep = Dependency(
        id=uuid.uuid4(),
        source_item_id=items[0].id,
        target_item_id=items[1].id,
        dependency_type="blocks",
    )
    db_session.add(dep)
    await db_session.commit()

    # Benchmark evaluation execution time
    start_t = time.perf_counter()
    eval_res = await RiskEngineService.evaluate_project(db_session, proj.id)
    elapsed_ms = (time.perf_counter() - start_t) * 1000

    # Ensure deterministic execution is lightning fast (< 500ms)
    assert elapsed_ms < 500.0, f"Evaluation took {elapsed_ms:.2f}ms, expected < 500ms"

    # Verify high/critical project risk detected
    assert eval_res.overall_severity.value in ("high", "critical")
    assert eval_res.total_signals >= 4
    assert eval_res.created_risks_count >= 4
