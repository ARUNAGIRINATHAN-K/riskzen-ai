import uuid
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import DataSource, Project


@pytest.mark.asyncio
async def test_create_project(db_session: AsyncSession):
    """Test creating and retrieving a Project record."""
    project = Project(
        name="Test Monitored System",
        description="Testing Phase 0 database model",
        project_type="software",
        status="active",
        health="green",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    assert project.id is not None
    assert isinstance(project.id, uuid.UUID)
    assert project.name == "Test Monitored System"
    assert project.health == "green"
    assert project.created_at is not None
    assert project.updated_at is not None

    # Query back
    stmt = select(Project).where(Project.id == project.id)
    result = await db_session.execute(stmt)
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert fetched.name == "Test Monitored System"


@pytest.mark.asyncio
async def test_project_with_data_source(db_session: AsyncSession):
    """Test creating a project with associated DataSource."""
    project = Project(
        name="GitHub Monitored Repo",
        description="Repo with connected GitHub source",
        status="active",
        health="green",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    data_source = DataSource(
        project_id=project.id,
        source_type="github",
        config={"repo": "owner/sample-repo"},
        status="connected",
    )
    db_session.add(data_source)
    await db_session.commit()

    # Query project with data sources
    stmt = select(Project).where(Project.id == project.id)
    result = await db_session.execute(stmt)
    fetched_project = result.scalar_one_or_none()

    assert fetched_project is not None
    assert len(fetched_project.data_sources) == 1
    assert fetched_project.data_sources[0].source_type == "github"
    assert fetched_project.data_sources[0].config["repo"] == "owner/sample-repo"
