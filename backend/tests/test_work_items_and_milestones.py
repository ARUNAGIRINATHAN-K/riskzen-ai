import uuid
from datetime import date
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_work_items_and_milestones_flow(client: AsyncClient):
    """Test creating milestones, work items, dependencies, and timeline API."""
    # 1. Create a project
    p_res = await client.post("/api/v1/projects", json={"name": "Timeline Test Project"})
    project_id = p_res.json()["id"]

    # 2. Create a Milestone
    m_res = await client.post(
        f"/api/v1/projects/{project_id}/milestones",
        json={
            "title": "Sprint 1: Core Infra",
            "target_date": "2026-10-30",
            "status": "open",
        },
    )
    assert m_res.status_code == 201
    milestone_id = m_res.json()["id"]

    # 3. Create Work Items
    wi1_res = await client.post(
        f"/api/v1/projects/{project_id}/work-items",
        json={
            "title": "Setup PostgreSQL Database",
            "milestone_id": milestone_id,
            "status": "done",
            "priority": "high",
            "assignee": "Alex",
        },
    )
    assert wi1_res.status_code == 201
    wi1_id = wi1_res.json()["id"]

    wi2_res = await client.post(
        f"/api/v1/projects/{project_id}/work-items",
        json={
            "title": "Implement API Auth",
            "milestone_id": milestone_id,
            "status": "open",
            "priority": "critical",
            "assignee": "Priya",
        },
    )
    assert wi2_res.status_code == 201
    wi2_id = wi2_res.json()["id"]

    # 4. Declare Dependency: WI2 is blocked by WI1
    dep_res = await client.post(
        f"/api/v1/projects/{project_id}/dependencies",
        json={
            "source_item_id": wi2_id,
            "target_item_id": wi1_id,
            "dependency_type": "blocks",
        },
    )
    assert dep_res.status_code == 201
    dep_id = dep_res.json()["id"]

    # 5. List Dependencies
    deps_list = await client.get(f"/api/v1/projects/{project_id}/dependencies")
    assert deps_list.status_code == 200
    assert len(deps_list.json()) == 1

    # 6. Check Timeline API
    timeline_res = await client.get(f"/api/v1/projects/{project_id}/timeline")
    assert timeline_res.status_code == 200
    timeline = timeline_res.json()
    assert len(timeline) == 1
    assert timeline[0]["milestone"]["title"] == "Sprint 1: Core Infra"
    assert timeline[0]["milestone"]["work_items_count"] == 2
    assert timeline[0]["milestone"]["completed_items_count"] == 1
    assert timeline[0]["milestone"]["completion_percent"] == 50.0

    # 7. Resolve Dependency
    resolve_res = await client.patch(
        f"/api/v1/projects/{project_id}/dependencies/{dep_id}/resolve"
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "resolved"
