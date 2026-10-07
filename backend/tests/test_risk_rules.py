"""Unit tests for all deterministic risk detection rules across 7 categories."""
import uuid
from datetime import datetime, timedelta, timezone
import pytest

from app.models.dependency import Dependency
from app.models.milestone import Milestone
from app.models.project import Project, ProjectMember
from app.models.risk import RiskCategory, RiskSeverity
from app.models.work_item import WorkItem
from app.risk_engine.base_rule import ProjectState
from app.risk_engine.rules.budget import BudgetVarianceRule, BurnRateAccelerationRule
from app.risk_engine.rules.capacity import (
    ExcessiveWIPRule,
    SingleOwnerBottleneckRule,
    WorkloadConcentrationRule,
)
from app.risk_engine.rules.decision import LongRunningBlockersRule, StalledPRReviewsRule
from app.risk_engine.rules.dependency import (
    BlockedTasksRule,
    DependencyConcentrationRule,
    OverdueUpstreamDependenciesRule,
)
from app.risk_engine.rules.quality import (
    CriticalDefectDebtRule,
    DefectGrowthRule,
    ReopenedIssuesRule,
)
from app.risk_engine.rules.schedule import (
    AgingWorkRule,
    MilestoneSlippageRule,
    OverdueTasksRule,
)
from app.risk_engine.rules.scope import RequirementChurnRule, ScopeGrowthRule
from app.risk_engine.thresholds import DEFAULT_THRESHOLDS


@pytest.fixture
def base_project():
    return Project(
        id=uuid.uuid4(),
        name="Test Project",
        key="TP",
        status="active",
        settings={},
    )


def test_schedule_overdue_tasks_rule(base_project):
    """Test detection of overdue work items."""
    now = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    
    # Item 1: overdue by 5 days (open)
    item1 = WorkItem(
        id=uuid.uuid4(),
        project_id=base_project.id,
        title="Overdue Feature",
        status="in_progress",
        due_date=now - timedelta(days=5),
        priority="high",
    )
    # Item 2: overdue by 15 days (critical)
    item2 = WorkItem(
        id=uuid.uuid4(),
        project_id=base_project.id,
        title="Critically Overdue Task",
        status="open",
        due_date=now - timedelta(days=15),
        priority="critical",
    )
    # Item 3: closed overdue item (should not trigger)
    item3 = WorkItem(
        id=uuid.uuid4(),
        project_id=base_project.id,
        title="Resolved Overdue Task",
        status="done",
        due_date=now - timedelta(days=5),
    )

    state = ProjectState.build(
        project=base_project,
        milestones=[],
        work_items=[item1, item2, item3],
        dependencies=[],
        members=[],
        thresholds=DEFAULT_THRESHOLDS.copy(),
        evaluation_time=now,
    )

    rule = OverdueTasksRule()
    signals = rule.evaluate(state)

    assert len(signals) == 1
    assert signals[0].category == RiskCategory.SCHEDULE
    assert signals[0].signal_type == "OVERDUE_TASKS"
    assert signals[0].severity == RiskSeverity.HIGH
    assert len(signals[0].evidence) == 2


def test_schedule_milestone_slippage_rule(base_project):
    """Test milestone slippage detection when due date is past and items are incomplete."""
    now = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    m_id = uuid.uuid4()
    
    milestone = Milestone(
        id=m_id,
        project_id=base_project.id,
        title="Release v1.0",
        due_date=now - timedelta(days=2),
        status="open",
    )

    item1 = WorkItem(
        id=uuid.uuid4(),
        project_id=base_project.id,
        milestone_id=m_id,
        title="Core API",
        status="in_progress",
    )
    item2 = WorkItem(
        id=uuid.uuid4(),
        project_id=base_project.id,
        milestone_id=m_id,
        title="UI Shell",
        status="done",
    )

    state = ProjectState.build(
        project=base_project,
        milestones=[milestone],
        work_items=[item1, item2],
        dependencies=[],
        members=[],
        thresholds=DEFAULT_THRESHOLDS.copy(),
        evaluation_time=now,
    )

    rule = MilestoneSlippageRule()
    signals = rule.evaluate(state)

    assert len(signals) == 1
    assert signals[0].category == RiskCategory.SCHEDULE
    assert signals[0].severity == RiskSeverity.CRITICAL
    assert signals[0].affected_milestone_id == str(m_id)


def test_dependency_blocked_tasks_rule(base_project):
    """Test detection of blocked tasks having incomplete blockers."""
    now = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    task_a = WorkItem(id=uuid.uuid4(), project_id=base_project.id, title="Task A (Blocker)", status="in_progress")
    task_b = WorkItem(id=uuid.uuid4(), project_id=base_project.id, title="Task B (Blocked)", status="open")
    
    dep = Dependency(
        id=uuid.uuid4(),
        source_item_id=task_a.id,
        target_item_id=task_b.id,
        dependency_type="blocks",
    )

    state = ProjectState.build(
        project=base_project,
        milestones=[],
        work_items=[task_a, task_b],
        dependencies=[dep],
        members=[],
        thresholds=DEFAULT_THRESHOLDS.copy(),
        evaluation_time=now,
    )

    rule = BlockedTasksRule()
    signals = rule.evaluate(state)

    assert len(signals) == 1
    assert signals[0].category == RiskCategory.DEPENDENCY
    assert signals[0].signal_type == "BLOCKED_WORK_ITEMS"


def test_scope_growth_rule(base_project):
    """Test milestone scope growth detection."""
    now = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    m_id = uuid.uuid4()
    start_date = now - timedelta(days=10)

    milestone = Milestone(
        id=m_id,
        project_id=base_project.id,
        title="Sprint 1",
        start_date=start_date,
        due_date=now + timedelta(days=10),
        status="open",
    )

    # 2 initial items
    items = [
        WorkItem(
            id=uuid.uuid4(),
            project_id=base_project.id,
            milestone_id=m_id,
            title=f"Initial {i}",
            created_at=start_date - timedelta(days=1),
            status="open",
        )
        for i in range(2)
    ]
    # 2 added items mid-sprint (100% growth)
    items.extend([
        WorkItem(
            id=uuid.uuid4(),
            project_id=base_project.id,
            milestone_id=m_id,
            title=f"Added {i}",
            created_at=now - timedelta(days=2),
            status="open",
        )
        for i in range(2)
    ])

    state = ProjectState.build(
        project=base_project,
        milestones=[milestone],
        work_items=items,
        dependencies=[],
        members=[],
        thresholds=DEFAULT_THRESHOLDS.copy(),
        evaluation_time=now,
    )

    rule = ScopeGrowthRule()
    signals = rule.evaluate(state)

    assert any(s.signal_type == "MILESTONE_SCOPE_CREEP" for s in signals)


def test_capacity_concentration_rule(base_project):
    """Test workload concentration on a single assignee."""
    now = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    assignee_1 = uuid.uuid4()
    assignee_2 = uuid.uuid4()

    # 8 items on assignee 1, 2 items on assignee 2 (80% concentration)
    items = [
        WorkItem(
            id=uuid.uuid4(),
            project_id=base_project.id,
            title=f"Task {i}",
            assignee_id=assignee_1,
            status="in_progress",
        )
        for i in range(8)
    ]
    items.extend([
        WorkItem(
            id=uuid.uuid4(),
            project_id=base_project.id,
            title=f"Task Other {i}",
            assignee_id=assignee_2,
            status="in_progress",
        )
        for i in range(2)
    ])

    state = ProjectState.build(
        project=base_project,
        milestones=[],
        work_items=items,
        dependencies=[],
        members=[],
        thresholds=DEFAULT_THRESHOLDS.copy(),
        evaluation_time=now,
    )

    rule = WorkloadConcentrationRule()
    signals = rule.evaluate(state)

    assert len(signals) == 1
    assert signals[0].category == RiskCategory.CAPACITY
    assert signals[0].signal_type == "WORKLOAD_CONCENTRATION"
    assert signals[0].severity == RiskSeverity.HIGH


def test_quality_critical_defect_debt_rule(base_project):
    """Test critical defect SLA breach detection."""
    now = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    
    # Bug open for 14 days (SLA is 7 days)
    bug = WorkItem(
        id=uuid.uuid4(),
        project_id=base_project.id,
        title="Critical Security Vulnerability",
        item_type="bug",
        priority="critical",
        status="open",
        created_at=now - timedelta(days=14),
    )

    state = ProjectState.build(
        project=base_project,
        milestones=[],
        work_items=[bug],
        dependencies=[],
        members=[],
        thresholds=DEFAULT_THRESHOLDS.copy(),
        evaluation_time=now,
    )

    rule = CriticalDefectDebtRule()
    signals = rule.evaluate(state)

    assert len(signals) == 1
    assert signals[0].category == RiskCategory.QUALITY
    assert signals[0].signal_type == "CRITICAL_DEFECT_DEBT"
    assert signals[0].severity == RiskSeverity.HIGH


def test_decision_long_running_blockers_rule(base_project):
    """Test long-running blocker detection."""
    now = datetime(2026, 10, 6, 12, 0, 0, tzinfo=timezone.utc)
    
    # Task blocked for 10 days (threshold is 5 days)
    item = WorkItem(
        id=uuid.uuid4(),
        project_id=base_project.id,
        title="Architecture Decision on Auth",
        status="blocked",
        updated_at=now - timedelta(days=10),
    )

    state = ProjectState.build(
        project=base_project,
        milestones=[],
        work_items=[item],
        dependencies=[],
        members=[],
        thresholds=DEFAULT_THRESHOLDS.copy(),
        evaluation_time=now,
    )

    rule = LongRunningBlockersRule()
    signals = rule.evaluate(state)

    assert len(signals) == 1
    assert signals[0].category == RiskCategory.DECISION
    assert signals[0].signal_type == "PROTRACTED_BLOCKER"
