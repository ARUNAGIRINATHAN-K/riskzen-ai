"""Unit tests for LangGraph 5-node risk investigation workflow."""
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.graph import build_investigation_graph
from app.agent.llm.mock import MockLLMProvider
from app.agent.state import InvestigationState
from app.models.dependency import Dependency
from app.models.milestone import Milestone
from app.models.project import Project
from app.models.work_item import WorkItem


@pytest.mark.asyncio
async def test_langgraph_investigation_workflow_execution(db_session: AsyncSession):
    """Test full LangGraph execution across investigate, retrieve_evidence, analyze, recommend, and review nodes."""
    # 1. Setup seed project data
    now = datetime.now(timezone.utc)
    proj = Project(
        id=uuid.uuid4(),
        name="LangGraph Test Project",
        key="LGTP",
        status="active",
        settings={},
    )
    db_session.add(proj)
    await db_session.flush()

    ms = Milestone(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="Sprint Alpha",
        due_date=now - timedelta(days=2),
        status="open",
    )
    db_session.add(ms)

    item1 = WorkItem(
        id=uuid.uuid4(),
        project_id=proj.id,
        milestone_id=ms.id,
        title="Payment Gateway Integration",
        status="in_progress",
        due_date=now - timedelta(days=5),
        priority="critical",
    )
    item2 = WorkItem(
        id=uuid.uuid4(),
        project_id=proj.id,
        milestone_id=ms.id,
        title="Checkout Confirmation UI",
        status="open",
        priority="high",
    )
    db_session.add_all([item1, item2])
    await db_session.flush()

    dep = Dependency(
        id=uuid.uuid4(),
        source_item_id=item1.id,
        target_item_id=item2.id,
        dependency_type="blocks",
    )
    db_session.add(dep)
    await db_session.commit()

    # 2. Build initial state
    initial_state: InvestigationState = {
        "risk_event_id": str(uuid.uuid4()),
        "project_id": str(proj.id),
        "risk_title": "Cascading Milestone Slippage & Blocked Tasks",
        "risk_category": "schedule",
        "risk_severity": "critical",
        "affected_milestone_id": str(ms.id),
        "risk_signals": [
            {
                "rule_id": "SCHEDULE_MILESTONE_SLIPPAGE_002",
                "signal_type": "MILESTONE_SLIPPAGE",
                "severity": "critical",
                "score": 0.85,
                "description": "Milestone is 2 days overdue with incomplete tasks.",
            }
        ],
        "project_context": {
            "project_name": proj.name,
            "total_work_items": 2,
            "overdue_items_count": 1,
            "active_members_count": 2,
            "milestones_summary": [f"{ms.title} (due {ms.due_date})"],
            "team_members": [{"name": "Lead Engineer", "role": "Tech Lead"}],
        },
        "initial_hypothesis": "",
        "scope_of_investigation": "",
        "key_questions": [],
        "evidence_queries": ["payment gateway", "checkout confirmation"],
        "retrieved_evidence": [],
        "explanation": "",
        "contributing_factors": [],
        "analysis_confidence": 0.0,
        "recommendations": [],
        "quality_check_passed": True,
        "review_feedback": "",
        "hallucination_detected": False,
        "retry_count": 0,
        "error": None,
    }

    # 3. Compile Graph with Mock LLM
    llm = MockLLMProvider()
    graph = build_investigation_graph(db_session, llm)

    # 4. Invoke graph
    final_state = await graph.ainvoke(initial_state)

    # 5. Assertions
    assert final_state["initial_hypothesis"] != ""
    assert len(final_state["retrieved_evidence"]) > 0
    assert final_state["explanation"] != ""
    assert len(final_state["contributing_factors"]) > 0
    assert len(final_state["recommendations"]) >= 2
    assert final_state["quality_check_passed"] is True
    assert final_state["analysis_confidence"] > 0.70
