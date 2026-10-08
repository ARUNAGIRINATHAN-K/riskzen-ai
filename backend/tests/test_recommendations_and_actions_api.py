"""Integration tests for Recommendation Approval, Action Tracking, and Outcome APIs."""
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.recommendation import Action, Recommendation
from app.models.risk import RiskCategory, RiskEvent, RiskSeverity, RiskStatus


@pytest.mark.asyncio
async def test_recommendations_and_actions_api_workflow(client: AsyncClient, db_session: AsyncSession):
    """Test full API lifecycle: investigate -> list recs -> approve -> list actions -> complete action -> record outcome."""
    # 1. Create project and risk event
    proj = Project(
        id=uuid.uuid4(),
        name="Action Test Project",
        key="ACTP",
        status="active",
        settings={},
    )
    db_session.add(proj)
    await db_session.flush()

    risk = RiskEvent(
        id=uuid.uuid4(),
        project_id=proj.id,
        category=RiskCategory.CAPACITY,
        severity=RiskSeverity.HIGH,
        propensity_score=0.75,
        confidence=0.85,
        status=RiskStatus.ACTIVE,
        title="Developer Workload Concentration Risk",
        description="Single engineer assigned 80% of active tasks.",
    )
    db_session.add(risk)
    await db_session.commit()

    # 2. Trigger AI Agent Investigation
    inv_resp = await client.post(f"/api/v1/risks/{risk.id}/investigate")
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()
    assert inv_data["status"] == "completed"
    assert inv_data["recommendations_count"] >= 1
    assert len(inv_data["recommendations"]) >= 1

    rec_id = inv_data["recommendations"][0]["id"]

    # 3. List recommendations
    list_rec_resp = await client.get(f"/api/v1/risks/{risk.id}/recommendations")
    assert list_rec_resp.status_code == 200
    recs = list_rec_resp.json()
    assert len(recs) >= 1

    # 4. Approve recommendation -> converts to Action
    approve_resp = await client.post(
        f"/api/v1/recommendations/{rec_id}/approve",
        json={"owner": "Senior Lead", "due_date": "2026-10-20"},
    )
    assert approve_resp.status_code == 200
    action_data = approve_resp.json()
    assert action_data["owner"] == "Senior Lead"
    assert action_data["status"] == "pending"
    action_id = action_data["id"]

    # 5. List project actions
    actions_resp = await client.get(f"/api/v1/projects/{proj.id}/actions")
    assert actions_resp.status_code == 200
    actions_list = actions_resp.json()
    assert actions_list["total_actions"] == 1
    assert actions_list["open_actions"] == 1

    # 6. Complete Action
    complete_resp = await client.post(f"/api/v1/actions/{action_id}/complete")
    assert complete_resp.status_code == 200
    completed_data = complete_resp.json()
    assert completed_data["status"] == "completed"

    # 7. Record Outcome
    outcome_resp = await client.post(
        f"/api/v1/risks/{risk.id}/outcome",
        json={"result": "yes", "feedback_comment": "Rebalancing tasks relieved developer pressure."},
    )
    assert outcome_resp.status_code == 200
    outcome_data = outcome_resp.json()
    assert outcome_data["result"] == "yes"

    # 8. Submit user feedback rating
    feedback_resp = await client.post(
        f"/api/v1/risks/{risk.id}/feedback",
        json={"rating": 5, "relevance": "relevant", "comment": "Accurate early detection."},
    )
    assert feedback_resp.status_code == 200
    feedback_data = feedback_resp.json()
    assert feedback_data["rating"] == 5


@pytest.mark.asyncio
async def test_recommendation_modify_dismiss_snooze(client: AsyncClient, db_session: AsyncSession):
    """Test modify, dismiss, and snooze actions on recommendations."""
    proj = Project(
        id=uuid.uuid4(),
        name="Decision Test Project",
        key="DTP",
        status="active",
        settings={},
    )
    db_session.add(proj)
    await db_session.flush()

    risk = RiskEvent(
        id=uuid.uuid4(),
        project_id=proj.id,
        category=RiskCategory.DECISION,
        severity=RiskSeverity.MEDIUM,
        propensity_score=0.50,
        status=RiskStatus.ACTIVE,
        title="Stalled Decision Risk",
    )
    db_session.add(risk)
    await db_session.flush()

    rec1 = Recommendation(
        id=uuid.uuid4(),
        risk_event_id=risk.id,
        action_description="Hold sync with architect",
        rationale="Unblocks decision",
        suggested_owner="Tech Lead",
        urgency="today",
        status="pending",
    )
    rec2 = Recommendation(
        id=uuid.uuid4(),
        risk_event_id=risk.id,
        action_description="Postpone release date",
        rationale="Gain buffer",
        suggested_owner="PM",
        urgency="optional",
        status="pending",
    )
    rec3 = Recommendation(
        id=uuid.uuid4(),
        risk_event_id=risk.id,
        action_description="Snooze alert check",
        rationale="Wait for PR review",
        suggested_owner="PM",
        urgency="this_week",
        status="pending",
    )
    db_session.add_all([rec1, rec2, rec3])
    await db_session.commit()

    # Modify rec1
    mod_resp = await client.post(
        f"/api/v1/recommendations/{rec1.id}/modify",
        json={
            "action_description": "Schedule immediate architectural review meeting",
            "owner": "Chief Architect",
            "reason": "Escalated priority to chief architect",
        },
    )
    assert mod_resp.status_code == 200

    # Dismiss rec2
    dis_resp = await client.post(
        f"/api/v1/recommendations/{rec2.id}/dismiss",
        json={"reason": "Cannot postpone hard business deadline"},
    )
    assert dis_resp.status_code == 200
    assert dis_resp.json()["status"] == "dismissed"

    # Snooze rec3
    snooze_resp = await client.post(
        f"/api/v1/recommendations/{rec3.id}/snooze",
        json={"snooze_hours": 48, "reason": "Awaiting PR author response"},
    )
    assert snooze_resp.status_code == 200
    assert snooze_resp.json()["status"] == "snoozed"
    assert snooze_resp.json()["snooze_until"] is not None
