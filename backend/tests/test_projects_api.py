import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_project_crud_and_summary(client: AsyncClient):
    """Test full Project lifecycle via REST API."""
    # 1. Create project
    create_payload = {
        "name": "NovaPay Core Checkout",
        "description": "Payment checkout redesign",
        "project_type": "software",
    }
    create_res = await client.post("/api/v1/projects", json=create_payload)
    assert create_res.status_code == 201
    created = create_res.json()
    project_id = created["id"]
    assert created["name"] == "NovaPay Core Checkout"
    assert created["status"] == "active"
    assert created["health"] == "green"

    # 2. Get project by ID
    get_res = await client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == project_id

    # 3. List projects with pagination
    list_res = await client.get("/api/v1/projects", params={"page": 1, "per_page": 10})
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(p["id"] == project_id for p in list_data["items"])

    # 4. Update project status and health
    update_res = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={"health": "yellow", "description": "Updated description"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["health"] == "yellow"
    assert update_res.json()["description"] == "Updated description"

    # 5. Register Data Source
    ds_res = await client.post(
        f"/api/v1/projects/{project_id}/sources",
        json={"source_type": "github", "config": {"repo": "novapay/checkout"}},
    )
    assert ds_res.status_code == 201
    assert ds_res.json()["source_type"] == "github"

    # 6. List Data Sources
    ds_list_res = await client.get(f"/api/v1/projects/{project_id}/sources")
    assert ds_list_res.status_code == 200
    assert len(ds_list_res.json()) == 1

    # 7. Get Project Summary
    summary_res = await client.get(f"/api/v1/projects/{project_id}/summary")
    assert summary_res.status_code == 200
    summary_data = summary_res.json()
    assert summary_data["project"]["id"] == project_id
    assert "counts" in summary_data
    assert summary_data["counts"]["total_work_items"] == 0

    # 8. Delete Project
    del_res = await client.delete(f"/api/v1/projects/{project_id}")
    assert del_res.status_code == 204

    # Verify not found after delete
    get_after_del = await client.get(f"/api/v1/projects/{project_id}")
    assert get_after_del.status_code == 404
