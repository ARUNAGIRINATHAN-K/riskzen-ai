import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_budget_upload_and_snapshots(client: AsyncClient):
    """Test CSV budget upload endpoint, summary, and snapshot capture."""
    # 1. Create a project
    p_res = await client.post("/api/v1/projects", json={"name": "Budget & Snapshot Test"})
    project_id = p_res.json()["id"]

    # 2. Upload CSV Budget
    csv_content = """period,category,planned,actual,currency
2026-10,Engineering,45000,48000,USD
2026-10,Infrastructure,6000,5500,USD
"""
    files = {"file": ("q4_budget.csv", csv_content.encode("utf-8"), "text/csv")}
    upload_res = await client.post(f"/api/v1/projects/{project_id}/budget/upload", files=files)
    assert upload_res.status_code == 201
    records = upload_res.json()
    assert len(records) == 2
    assert records[0]["planned_amount"] == 45000.0

    # 3. Get Budget Summary
    summary_res = await client.get(f"/api/v1/projects/{project_id}/budget/summary")
    assert summary_res.status_code == 200
    b_summary = summary_res.json()
    assert b_summary["total_planned"] == 51000.0
    assert b_summary["total_actual"] == 53500.0
    assert b_summary["total_variance"] == 2500.0

    # 4. Capture Snapshot
    snap_create_res = await client.post(f"/api/v1/projects/{project_id}/snapshots")
    assert snap_create_res.status_code == 201
    snap = snap_create_res.json()
    assert snap["project_id"] == project_id
    assert "metrics_summary" in snap

    # 5. List Snapshots
    snap_list_res = await client.get(f"/api/v1/projects/{project_id}/snapshots")
    assert snap_list_res.status_code == 200
    assert len(snap_list_res.json()) >= 1
