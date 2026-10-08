"""End-to-end integration tests for AI agent risk investigation and audit trails."""
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.milestone import Milestone
from app.models.project import Project, ProjectMember
from app.models.recommendation import Action, Outcome, Recommendation
from app.models.risk import RiskCategory, RiskEvent, RiskSeverity, RiskStatus
from app.models.work_item import WorkItem
from app.services.agent_service import AgentService
from app.services.risk_engine_service import RiskEngineService


@pytest.mark.asyncio
async def test_end_to_end_data_to_agent_investigation_flow(db_session: AsyncSession):
    """Verifies complete end-to-end flow:
    1. Seed project with severe delays
    2. Deterministic Risk Engine detects high-severity risk
    3. Auto-triggers LangGraph agent investigation
    4. Recommendations generated with grounded evidence citations
    5. Recommendation approved -> Action created -> Action completed
    6. Outcome recorded
    7. Complete audit trail verified
    """
    now = datetime.now(timezone.utc)
    proj = Project(
        id=uuid.uuid4(),
        name="E2E Agent Flow Project",
        key="E2E",
        status="active",
        settings={},
    )
    db_session.add(proj)
    await db_session.flush()

    # Add team member
    member = ProjectMember(
        id=uuid.uuid4(), project_id=proj.id, user_id=uuid.uuid4(), role="Tech Lead"
    )
    db_session.add(member)

    # Add overdue milestone and work items
    ms = Milestone(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="Payment Release",
        due_date=now - timedelta(days=4),
        status="open",
    )
    db_session.add(ms)

    for i in range(5):
        db_session.add(
            WorkItem(
                id=uuid.uuid4(),
                project_id=proj.id,
                milestone_id=ms.id,
                title=f"Core Processing Step {i}",
                status="in_progress",
                due_date=now - timedelta(days=6),
                priority="critical",
                assignee_id=member.user_id,
            )
        )
    await db_session.commit()

    # Step 1: Run Risk Engine Evaluation (which auto-triggers Agent investigation for material risks)
    eval_resp = await RiskEngineService.evaluate_project(db_session, proj.id)
    assert eval_resp.overall_severity.value in ("high", "critical")

    # Step 2: Verify Risk Event & Recommendations exist
    risks = await RiskEngineService.list_project_risks(db_session, proj.id)
    assert len(risks) >= 1
    material_risk = risks[0]

    recs = await AgentService.list_risk_recommendations(db_session, material_risk.id)
    assert len(recs) >= 1
    rec = recs[0]

    # Step 3: Approve recommendation
    from app.schemas.recommendation import RecommendationApproveRequest
    action = await AgentService.approve_recommendation(
        db_session, rec.id, RecommendationApproveRequest(owner="Tech Lead"), actor="pm_user"
    )
    assert action.status == "pending"

    # Step 4: Complete action
    completed_action = await AgentService.complete_action(db_session, action.id, actor="pm_user")
    assert completed_action.status == "completed"

    # Step 5: Record outcome
    from app.schemas.outcome import OutcomeCreate
    outcome = await AgentService.record_outcome(
        db_session, material_risk.id, OutcomeCreate(result="yes", feedback_comment="Successfully unblocked payment release"), actor="pm_user"
    )
    assert outcome.result == "yes"

    # Step 6: Verify full audit trail
    audit_stmt = select(AuditLog).where(AuditLog.project_id == proj.id).order_by(AuditLog.created_at.asc())
    audit_res = await db_session.execute(audit_stmt)
    audit_logs = audit_res.scalars().all()
    event_types = [a.event_type for a in audit_logs]

    assert "risk_investigated" in event_types
    assert "recommendation_approved" in event_types
    assert "action_completed" in event_types
    assert "outcome_recorded" in event_types
