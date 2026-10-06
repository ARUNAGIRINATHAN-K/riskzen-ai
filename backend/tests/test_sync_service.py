import uuid
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.connectors.base import SyncResult
from app.models.project import DataSource, Project
from app.services.sync_service import SyncService


@pytest.mark.asyncio
async def test_sync_service_github_mocked(client: AsyncClient, db_session: AsyncSession):
    """Test full SyncService orchestration with mocked GitHub API results."""
    # 1. Create project with GitHub DataSource
    project = Project(name="Sync Test Project")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    data_source = DataSource(
        project_id=project.id,
        source_type="github",
        config={"repo": "testowner/testrepo"},
        status="connected",
    )
    db_session.add(data_source)
    await db_session.commit()
    await db_session.refresh(data_source)

    mock_result = SyncResult(
        success=True,
        items_created=2,
        milestones_synced=1,
        details={
            "milestones": [
                {
                    "external_id": "ms-100",
                    "title": "Alpha Release",
                    "status": "open",
                    "completion_percent": 0.0,
                }
            ],
            "work_items": [
                {
                    "external_id": "gh-1",
                    "title": "Setup CI/CD Pipeline",
                    "status": "done",
                    "priority": "high",
                    "milestone_external_id": "ms-100",
                },
                {
                    "external_id": "gh-2",
                    "title": "Deploy to Staging",
                    "status": "open",
                    "priority": "critical",
                    "milestone_external_id": "ms-100",
                },
            ],
            "dependencies": [
                {
                    "source_external_id": "gh-2",
                    "target_external_id": "gh-1",
                    "dependency_type": "blocks",
                }
            ],
        },
    )

    with patch("app.connectors.github.GitHubConnector.sync", new_callable=AsyncMock) as mock_sync:
        mock_sync.return_value = mock_result

        # Trigger sync
        jobs = await SyncService.execute_sync(db_session, project_id=project.id)

        assert len(jobs) == 1
        assert jobs[0].status == "completed"
        assert jobs[0].items_synced == 3

    # Verify sync history endpoint via API
    hist_res = await client.get(f"/api/v1/projects/{project.id}/sync-history")
    assert hist_res.status_code == 200
    history = hist_res.json()
    assert len(history) >= 1
    assert history[0]["status"] == "completed"
