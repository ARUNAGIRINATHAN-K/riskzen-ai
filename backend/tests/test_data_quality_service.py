import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.work_item import Milestone, WorkItem
from app.services.data_quality_service import DataQualityService


@pytest.mark.asyncio
async def test_data_quality_evaluation_and_api(client: AsyncClient, db_session: AsyncSession):
    """Test data quality checks and composite scoring."""
    # 1. Create a project
    project = Project(name="Data Quality Test Project")
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # 2. Add work items: 1 with due date, 1 without due date
    wi_with_due = WorkItem(
        project_id=project.id,
        title="Task with due date",
        status="open",
        due_date=None,  # missing
    )
    db_session.add(wi_with_due)
    await db_session.commit()

    # 3. Evaluate Data Quality
    report = await DataQualityService.evaluate_data_quality(db_session, project.id)

    assert report.project_id == project.id
    assert 0.0 <= report.overall_score <= 100.0
    assert len(report.checks) == 5

    # Check check types exist
    check_types = [c.check_type for c in report.checks]
    assert "missing_due_dates" in check_types
    assert "stale_items" in check_types
    assert "missing_target_dates" in check_types
    assert "unresolved_deps" in check_types
    assert "budget_coverage" in check_types

    # 4. Test REST API endpoint
    api_res = await client.get(f"/api/v1/projects/{project.id}/data-quality")
    assert api_res.status_code == 200
    api_data = api_res.json()
    assert api_data["project_id"] == str(project.id)
    assert len(api_data["checks"]) == 5
