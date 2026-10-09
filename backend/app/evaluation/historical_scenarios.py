"""Historical Project Scenarios for Risk Detection & AI Investigation Evaluation.

Provides 3 realistic, reproducible historical scenarios with known ground truth risk outcomes:
- Scenario A: Schedule slippage due to blocked dependency cascade (Critical Schedule & Dependency Risks)
- Scenario B: Scope creep & requirement churn causing delivery risk (High Scope & Capacity Risks)
- Scenario C: Healthy sprint execution with minor issues (Low Risk, 0 Critical Alerts)
"""
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from app.models.budget import BudgetRecord
from app.models.project import Project, ProjectMember
from app.models.team import Team, TeamMember
from app.models.work_item import Dependency, Milestone, WorkItem
from app.risk_engine.base_rule import ProjectState


@dataclass
class GroundTruthRisk:
    """Expected risk signal for precision and recall calculation."""

    category: str
    signal_type: str
    expected_severity: str  # low, medium, high, critical
    impact_date: date
    description: str
    is_critical_or_high: bool = True


@dataclass
class HistoricalScenario:
    """A complete scenario package including state, metadata, and ground truth."""

    id: str
    name: str
    description: str
    target_date: date
    evaluation_date: date
    state: ProjectState
    ground_truth_risks: List[GroundTruthRisk]
    expected_healthy: bool = False


def create_scenario_a_blocked_dependency(base_date: Optional[date] = None) -> HistoricalScenario:
    """Scenario A: Schedule slippage caused by an overdue upstream dependency blocker.

    Ground Truth:
    - Schedule Risk: Milestone slippage & overdue tasks (Critical)
    - Dependency Risk: Blocked tasks & overdue upstream dependency (Critical)
    """
    today = base_date or date(2026, 10, 15)
    project_id = uuid.uuid4()
    milestone_id = uuid.uuid4()
    milestone_target = today + timedelta(days=5)

    project = Project(
        id=project_id,
        name="Scenario A: Checkout API Migration",
        key="SCEN-A",
        description="Core payment provider migration with external dependency blocker",
        status="active",
        health="critical",
        created_at=datetime.combine(today - timedelta(days=30), datetime.min.time(), tzinfo=timezone.utc),
    )

    milestone = Milestone(
        id=milestone_id,
        project_id=project_id,
        title="Payment Gateway V2 Cutover",
        description="Migrate payment routing to new gateway",
        status="open",
        target_date=milestone_target,
        start_date=today - timedelta(days=25),
        created_at=datetime.combine(today - timedelta(days=25), datetime.min.time(), tzinfo=timezone.utc),
    )

    member_alice = TeamMember(
        id=uuid.uuid4(),
        name="Alice Engineer",
        email="alice@riskzen.io",
        role="Backend Tech Lead",
    )
    member_bob = TeamMember(
        id=uuid.uuid4(),
        name="Bob Developer",
        email="bob@riskzen.io",
        role="Senior Software Engineer",
    )

    # 1. Upstream blocker task (Overdue by 8 days)
    upstream_task_id = uuid.uuid4()
    upstream_task = WorkItem(
        id=upstream_task_id,
        project_id=project_id,
        milestone_id=milestone_id,
        source_item_id="101",
        title="Implement OAuth2 Token Exchange with Bank Gateway",
        description="Required before payment tokenization API can function. Depends on bank API keys.",
        item_type="issue",
        status="in_progress",
        priority="critical",
        created_at=datetime.combine(today - timedelta(days=20), datetime.min.time(), tzinfo=timezone.utc),
        due_date=today - timedelta(days=8),
        assignee_name="Alice Engineer",
    )

    # 2. Downstream blocked tasks
    task_2_id = uuid.uuid4()
    task_2 = WorkItem(
        id=task_2_id,
        project_id=project_id,
        milestone_id=milestone_id,
        source_item_id="102",
        title="Integrate Vault 3DS Authentication Service",
        description="Blocked by OAuth2 Token Exchange",
        item_type="issue",
        status="blocked",
        priority="high",
        created_at=datetime.combine(today - timedelta(days=15), datetime.min.time(), tzinfo=timezone.utc),
        due_date=today + timedelta(days=2),
        assignee_name="Bob Developer",
    )

    task_3_id = uuid.uuid4()
    task_3 = WorkItem(
        id=task_3_id,
        project_id=project_id,
        milestone_id=milestone_id,
        source_item_id="103",
        title="End-to-End Payment Flow Smoke Tests",
        description="Blocked by Vault 3DS Integration",
        item_type="issue",
        status="blocked",
        priority="critical",
        created_at=datetime.combine(today - timedelta(days=10), datetime.min.time(), tzinfo=timezone.utc),
        due_date=today + timedelta(days=4),
        assignee_name="Alice Engineer",
    )

    # 3. Regular active task
    task_4 = WorkItem(
        id=uuid.uuid4(),
        project_id=project_id,
        milestone_id=milestone_id,
        source_item_id="104",
        title="Update Checkout UI Error Modals",
        description="Front-end banner updates",
        item_type="issue",
        status="in_progress",
        priority="medium",
        created_at=datetime.combine(today - timedelta(days=5), datetime.min.time(), tzinfo=timezone.utc),
        due_date=today + timedelta(days=3),
        assignee_name="Bob Developer",
    )

    # 4. Completed task
    task_5 = WorkItem(
        id=uuid.uuid4(),
        project_id=project_id,
        milestone_id=milestone_id,
        source_item_id="105",
        title="Database Schema Migration for Transaction Logs",
        description="Completed successfully",
        item_type="issue",
        status="closed",
        priority="medium",
        created_at=datetime.combine(today - timedelta(days=25), datetime.min.time(), tzinfo=timezone.utc),
        completed_at=datetime.combine(today - timedelta(days=18), datetime.min.time(), tzinfo=timezone.utc),
        due_date=today - timedelta(days=19),
        assignee_name="Alice Engineer",
    )

    # Dependencies
    dep_1 = Dependency(
        id=uuid.uuid4(),
        project_id=project_id,
        blocked_item_id=task_2_id,
        blocker_item_id=upstream_task_id,
        dependency_type="blocks",
    )
    dep_2 = Dependency(
        id=uuid.uuid4(),
        project_id=project_id,
        blocked_item_id=task_3_id,
        blocker_item_id=task_2_id,
        dependency_type="blocks",
    )

    state = ProjectState(
        project=project,
        milestones=[milestone],
        work_items=[upstream_task, task_2, task_3, task_4, task_5],
        dependencies=[dep_1, dep_2],
        budget_records=[],
        team_members=[member_alice, member_bob],
        data_quality_score=94.0,
        today=today,
    )

    ground_truth = [
        GroundTruthRisk(
            category="dependency",
            signal_type="blocked_tasks",
            expected_severity="critical",
            impact_date=milestone_target,
            description="2 downstream tasks blocked by overdue OAuth2 Token Exchange item",
        ),
        GroundTruthRisk(
            category="schedule",
            signal_type="overdue_tasks",
            expected_severity="high",
            impact_date=milestone_target,
            description="Critical upstream work item #101 is 8 days overdue",
        ),
    ]

    return HistoricalScenario(
        id="scenario_a_blocked_dependency",
        name="Scenario A: Blocked Dependency Cascade",
        description="Upstream OAuth2 implementation delay causing blocked downstream tasks and milestone slippage",
        target_date=milestone_target,
        evaluation_date=today,
        state=state,
        ground_truth_risks=ground_truth,
        expected_healthy=False,
    )


def create_scenario_b_scope_creep(base_date: Optional[date] = None) -> HistoricalScenario:
    """Scenario B: Scope creep & excessive WIP causing capacity overload near deadline.

    Ground Truth:
    - Scope Risk: Scope growth / requirement churn post milestone start (High/Critical)
    - Capacity Risk: Excessive WIP / Workload concentration on single developer (High)
    """
    today = base_date or date(2026, 10, 15)
    project_id = uuid.uuid4()
    milestone_id = uuid.uuid4()
    milestone_target = today + timedelta(days=6)

    project = Project(
        id=project_id,
        name="Scenario B: Analytics Pipeline Engine",
        key="SCEN-B",
        description="Real-time telemetry ingestion pipeline with massive late scope additions",
        status="active",
        health="at_risk",
        created_at=datetime.combine(today - timedelta(days=20), datetime.min.time(), tzinfo=timezone.utc),
    )

    milestone = Milestone(
        id=milestone_id,
        project_id=project_id,
        title="Sprint 14: Streaming Analytics MVP",
        description="Deliver Kafka-based streaming ingestion engine",
        status="open",
        target_date=milestone_target,
        start_date=today - timedelta(days=14),
        created_at=datetime.combine(today - timedelta(days=14), datetime.min.time(), tzinfo=timezone.utc),
    )

    member_carol = TeamMember(
        id=uuid.uuid4(),
        name="Carol Senior Dev",
        email="carol@riskzen.io",
        role="Lead Systems Engineer",
    )

    # Work items: 2 original items + 7 newly added items in the last 4 days (all assigned to Carol)
    work_items: List[WorkItem] = []

    # Original items
    work_items.append(
        WorkItem(
            id=uuid.uuid4(),
            project_id=project_id,
            milestone_id=milestone_id,
            source_item_id="201",
            title="Set up Kafka Topic Partitioning",
            description="Base streaming topic setup",
            item_type="issue",
            status="closed",
            priority="high",
            created_at=datetime.combine(today - timedelta(days=14), datetime.min.time(), tzinfo=timezone.utc),
            completed_at=datetime.combine(today - timedelta(days=8), datetime.min.time(), tzinfo=timezone.utc),
            due_date=today - timedelta(days=8),
            assignee_name="Carol Senior Dev",
        )
    )
    work_items.append(
        WorkItem(
            id=uuid.uuid4(),
            project_id=project_id,
            milestone_id=milestone_id,
            source_item_id="202",
            title="Build Consumer Worker Group",
            description="Core ingestion service",
            item_type="issue",
            status="in_progress",
            priority="critical",
            created_at=datetime.combine(today - timedelta(days=14), datetime.min.time(), tzinfo=timezone.utc),
            due_date=today + timedelta(days=3),
            assignee_name="Carol Senior Dev",
        )
    )

    # 6 Unplanned Scope Items injected mid-sprint
    for i in range(1, 7):
        work_items.append(
            WorkItem(
                id=uuid.uuid4(),
                project_id=project_id,
                milestone_id=milestone_id,
                source_item_id=f"20{i+2}",
                title=f"Unplanned Ad-hoc Feature Request #{i}: Custom Exporter",
                description="Late scope addition added without adjusting milestone end date.",
                item_type="issue",
                status="in_progress",
                priority="high" if i % 2 == 0 else "medium",
                created_at=datetime.combine(today - timedelta(days=2), datetime.min.time(), tzinfo=timezone.utc),
                due_date=today + timedelta(days=4),
                assignee_name="Carol Senior Dev",
            )
        )

    state = ProjectState(
        project=project,
        milestones=[milestone],
        work_items=work_items,
        dependencies=[],
        budget_records=[],
        team_members=[member_carol],
        data_quality_score=90.0,
        today=today,
    )

    ground_truth = [
        GroundTruthRisk(
            category="scope",
            signal_type="scope_growth",
            expected_severity="high",
            impact_date=milestone_target,
            description="6 items added after sprint start, representing >150% scope expansion",
        ),
        GroundTruthRisk(
            category="capacity",
            signal_type="workload_concentration",
            expected_severity="high",
            impact_date=milestone_target,
            description="100% of open work items concentrated on single engineer Carol",
        ),
    ]

    return HistoricalScenario(
        id="scenario_b_scope_creep",
        name="Scenario B: Mid-Sprint Scope Creep",
        description="Late scope injection with 7 concurrent in-progress items concentrated on one engineer",
        target_date=milestone_target,
        evaluation_date=today,
        state=state,
        ground_truth_risks=ground_truth,
        expected_healthy=False,
    )


def create_scenario_c_healthy_sprint(base_date: Optional[date] = None) -> HistoricalScenario:
    """Scenario C: Healthy sprint execution with minor issues.

    Ground Truth:
    - 0 Critical or High risks
    - No milestone slippage or blocked chains
    - Expected overall rating: Healthy
    """
    today = base_date or date(2026, 10, 15)
    project_id = uuid.uuid4()
    milestone_id = uuid.uuid4()
    milestone_target = today + timedelta(days=12)

    project = Project(
        id=project_id,
        name="Scenario C: Design System 2.0",
        key="SCEN-C",
        description="Component library upgrade executing smoothly on schedule",
        status="active",
        health="healthy",
        created_at=datetime.combine(today - timedelta(days=30), datetime.min.time(), tzinfo=timezone.utc),
    )

    milestone = Milestone(
        id=milestone_id,
        project_id=project_id,
        title="Sprint 8: UI Foundation",
        description="Core design tokens and accessible modal dialogs",
        status="open",
        target_date=milestone_target,
        start_date=today - timedelta(days=10),
        created_at=datetime.combine(today - timedelta(days=10), datetime.min.time(), tzinfo=timezone.utc),
    )

    member_dave = TeamMember(
        id=uuid.uuid4(),
        name="Dave UI Dev",
        email="dave@riskzen.io",
        role="Frontend Engineer",
    )
    member_emma = TeamMember(
        id=uuid.uuid4(),
        name="Emma UX Dev",
        email="emma@riskzen.io",
        role="Frontend Engineer",
    )

    # 8 Completed items + 2 In-Progress items with ample runway
    work_items: List[WorkItem] = []

    for i in range(1, 9):
        work_items.append(
            WorkItem(
                id=uuid.uuid4(),
                project_id=project_id,
                milestone_id=milestone_id,
                source_item_id=f"30{i}",
                title=f"Button and Card Component Token Set #{i}",
                description="Completed on schedule",
                item_type="issue",
                status="closed",
                priority="medium",
                created_at=datetime.combine(today - timedelta(days=10), datetime.min.time(), tzinfo=timezone.utc),
                completed_at=datetime.combine(today - timedelta(days=3), datetime.min.time(), tzinfo=timezone.utc),
                due_date=today - timedelta(days=2),
                assignee_name="Dave UI Dev" if i % 2 == 0 else "Emma UX Dev",
            )
        )

    # 2 Active in-progress items
    work_items.append(
        WorkItem(
            id=uuid.uuid4(),
            project_id=project_id,
            milestone_id=milestone_id,
            source_item_id="309",
            title="Accessible Dropdown Menu Navigation",
            description="Work underway, 70% complete",
            item_type="issue",
            status="in_progress",
            priority="medium",
            created_at=datetime.combine(today - timedelta(days=8), datetime.min.time(), tzinfo=timezone.utc),
            due_date=today + timedelta(days=8),
            assignee_name="Dave UI Dev",
        )
    )
    work_items.append(
        WorkItem(
            id=uuid.uuid4(),
            project_id=project_id,
            milestone_id=milestone_id,
            source_item_id="310",
            title="Tooltip Hover Delay Settings",
            description="Work underway",
            item_type="issue",
            status="in_progress",
            priority="low",
            created_at=datetime.combine(today - timedelta(days=8), datetime.min.time(), tzinfo=timezone.utc),
            due_date=today + timedelta(days=10),
            assignee_name="Emma UX Dev",
        )
    )

    state = ProjectState(
        project=project,
        milestones=[milestone],
        work_items=work_items,
        dependencies=[],
        budget_records=[],
        team_members=[member_dave, member_emma],
        data_quality_score=98.0,
        today=today,
    )

    return HistoricalScenario(
        id="scenario_c_healthy_sprint",
        name="Scenario C: Healthy Design System Sprint",
        description="80% completion rate, evenly distributed workload, zero blockers",
        target_date=milestone_target,
        evaluation_date=today,
        state=state,
        ground_truth_risks=[],
        expected_healthy=True,
    )


def get_all_historical_scenarios(base_date: Optional[date] = None) -> List[HistoricalScenario]:
    """Returns all 3 historical scenarios."""
    return [
        create_scenario_a_blocked_dependency(base_date),
        create_scenario_b_scope_creep(base_date),
        create_scenario_c_healthy_sprint(base_date),
    ]
