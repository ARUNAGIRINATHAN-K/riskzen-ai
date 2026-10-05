"""Initial schema: pgvector extension, projects, and data_sources tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension (if using PostgreSQL)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Create projects table
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_type", sa.String(length=50), nullable=False, server_default="software"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("health", sa.String(length=20), nullable=False, server_default="green"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_index("ix_projects_health", "projects", ["health"])

    # 3. Create data_sources table
    op.create_table(
        "data_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="connected"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_data_sources_project_id", "data_sources", ["project_id"])
    op.create_index("ix_data_sources_source_type", "data_sources", ["source_type"])


def downgrade() -> None:
    op.drop_index("ix_data_sources_source_type", table_name="data_sources")
    op.drop_index("ix_data_sources_project_id", table_name="data_sources")
    op.drop_table("data_sources")

    op.drop_index("ix_projects_health", table_name="projects")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_table("projects")

    # Optionally drop extension
    # op.execute("DROP EXTENSION IF EXISTS vector;")
