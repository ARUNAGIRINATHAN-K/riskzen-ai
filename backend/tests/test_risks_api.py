"""Integration tests for Risk Detection API endpoints."""
import uuid
from datetime import datetime, timedelta, timezone
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.milestone import Milestone
from app.models.project import Project
from app.models.risk import RiskCategory, RiskSeverity, RiskStatus
from app.models.work_item import WorkItem


@pytest.mark.asyncio
async def test_evaluate_and_list_risks_api(client: AsyncClient, db_session: AsyncSession):
    """Test POST /evaluate endpoint and GET /risks filtering."""
    # 1. Create project
    proj = Project(
        id=uuid.uuid4(),
        name="Risk API Test Project",
        key="RAP",
        status="active",
        settings={},
    )
    db_session.add(proj)
    await db_session.flush()

    # 2. Add overdue work items
    now = datetime.now(timezone.utc)
    wi1 = WorkItem(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="Delayed Core Module",
        status="in_progress",
        due_date=now - timedelta(days=6),
        priority="critical",
    )
    wi2 = WorkItem(
        id=uuid.uuid4(),
        project_id=proj.id,
        title="Stalled Bug Fix",
        status="open",
        due_date=now - timedelta(days=12),
        priority="high",
    )
    db_session.add_all([wi1, wi2])
    await db_session.commit()

    # 3. Trigger evaluation via API
    eval_resp = await client.post(f"/api/v1/projects/{proj.id}/evaluate")
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()
    assert eval_data["project_id"] == str(proj.id)
    assert eval_data["total_signals"] > 0
    assert eval_data["created_risks_count"] > 0
    assert eval_data["overall_score"] > 0.0

    # 4. List risks via API
    list_resp = await client.get(f"/api/v1/projects/{proj.id}/risks")
    assert list_resp.status_code == 200
    risks = list_resp.json()
    assert len(risks) >= 1
    risk_id = risks[0]["id"]

    # 5. Get risk detail
    detail_resp = await client.get(f"/api/v1/projects/{proj.id}/risks/{risk_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["id"] == risk_id
    assert len(detail["signals"]) >= 1
    assert len(detail["history"]) >= 1

    # 6. Update risk status (e.g. to mitigated)
    status_resp = await client.patch(
        f"/api/v1/projects/{proj.id}/risks/{risk_id}/status",
        json={"status": "mitigated", "reason": "Added extra engineer to address delay"},
    )
    assert status_resp.status_code == 200
    updated_detail = status_resp.json()
    assert updated_detail["status"] == "mitigated"
    assert len(updated_detail["history"]) >= 2

    # 7. Get risk summary
    summary_resp = await client.get(f"/api/v1/projects/{proj.id}/risk-summary")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["project_id"] == str(proj.id)
    assert "schedule" in summary["category_summaries"]


@pytest.mark.asyncio
async def test_thresholds_api(client: AsyncClient, db_session: AsyncSession):
    """Test GET and PUT /thresholds endpoints."""
    proj = Project(
        id=uuid.uuid4(),
        name="Thresholds Test Project",
        key="TTP",
        status="active",
        settings={},
    )
    db_session.add(proj)
    await db_session.commit()

    # Get default thresholds
    get_resp = await client.get(f"/api/v1/projects/{proj.id}/thresholds")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert len(data["thresholds"]) >= 7

    # Update threshold
    put_resp = await client.put(
        f"/api/v1/projects/{proj.id}/thresholds",
        json={"thresholds": {"overdue_task_days": 5.0, "scope_growth_rate": 0.30}},
    )
    assert put_resp.status_code == 200
    updated_data = put_resp.json()
    thresh_map = {t["name"]: t["value"] for t in updated_data["thresholds"]}
    assert thresh_map["overdue_task_days"] == 5.0
    assert thresh_map["scope_growth_rate"] == 0.30
