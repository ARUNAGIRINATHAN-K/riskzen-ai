"""Core data foundation: all 10 core entities and supporting tables

Revision ID: 002_core_data_foundation
Revises: 001_initial_schema
Create Date: 2026-10-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_core_data_foundation"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. milestones
    op.create_table(
        "milestones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("completion_percent", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_milestones_project_id", "milestones", ["project_id"])
    op.create_index("ix_milestones_external_id", "milestones", ["external_id"])

    # 2. work_items
    op.create_table(
        "work_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("milestone_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("milestones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("external_id", sa.String(length=100), nullable=True),
        sa.Column("source_type", sa.String(length=30), nullable=False, server_default="github"),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="open"),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("item_type", sa.String(length=30), nullable=False, server_default="task"),
        sa.Column("assignee", sa.String(length=200), nullable=True),
        sa.Column("labels", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cycle_time_hours", sa.Float(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_work_items_project_id", "work_items", ["project_id"])
    op.create_index("ix_work_items_milestone_id", "work_items", ["milestone_id"])
    op.create_index("ix_work_items_external_id", "work_items", ["external_id"])
    op.create_index("ix_work_items_assignee", "work_items", ["assignee"])
    op.create_index("ix_work_items_due_date", "work_items", ["due_date"])
    op.create_index("ix_work_items_project_status", "work_items", ["project_id", "status"])
    op.create_index("ix_work_items_project_priority", "work_items", ["project_id", "priority"])

    # 3. dependencies
    op.create_table(
        "dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("work_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dependency_type", sa.String(length=30), nullable=False, server_default="blocks"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_dependencies_project_id", "dependencies", ["project_id"])
    op.create_index("ix_dependencies_source_item_id", "dependencies", ["source_item_id"])
    op.create_index("ix_dependencies_target_item_id", "dependencies", ["target_item_id"])
    op.create_index("ix_dependencies_project_status", "dependencies", ["project_id", "status"])

    # 4. teams & team_members
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_teams_project_id", "teams", ["project_id"])

    op.create_table(
        "team_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=False, server_default="engineer"),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("github_username", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_team_members_team_id", "team_members", ["team_id"])
    op.create_index("ix_team_members_github_username", "team_members", ["github_username"])

    # 5. risk_events, risk_signals, evidence
    op.create_table(
        "risk_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("affected_milestone_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("milestones.id", ondelete="SET NULL"), nullable=True),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("confidence", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("agent_explanation", sa.Text(), nullable=True),
        sa.Column("agent_investigated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_risk_events_project_id", "risk_events", ["project_id"])
    op.create_index("ix_risk_events_affected_milestone_id", "risk_events", ["affected_milestone_id"])
    op.create_index("ix_risk_events_proj_stat_sev", "risk_events", ["project_id", "status", "severity"])
    op.create_index("ix_risk_events_detected_at", "risk_events", ["detected_at"])

    op.create_table(
        "risk_signals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("risk_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risk_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("signal_type", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_risk_signals_risk_event_id", "risk_signals", ["risk_event_id"])

    op.create_table(
        "evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("risk_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risk_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("reference_label", sa.String(length=200), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_evidence_risk_event_id", "evidence", ["risk_event_id"])

    # 6. recommendations, actions, outcomes
    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("risk_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risk_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action_description", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("suggested_owner", sa.String(length=200), nullable=True),
        sa.Column("urgency", sa.String(length=20), nullable=False, server_default="this_week"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("decision_reason", sa.Text(), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("snooze_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_recommendations_risk_event_id", "recommendations", ["risk_event_id"])

    op.create_table(
        "actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("recommendation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recommendations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("owner", sa.String(length=200), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_actions_project_id", "actions", ["project_id"])
    op.create_index("ix_actions_recommendation_id", "actions", ["recommendation_id"])
    op.create_index("ix_actions_project_status", "actions", ["project_id", "status"])

    op.create_table(
        "outcomes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("risk_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risk_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("feedback_comment", sa.Text(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_outcomes_risk_event_id", "outcomes", ["risk_event_id"], unique=True)

    # 7. budget_records, audit_logs, snapshots, data_quality, thresholds, sync_jobs, embeddings
    op.create_table(
        "budget_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("planned_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("actual_amount", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("variance", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="USD"),
        sa.Column("source_filename", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_budget_records_project_id", "budget_records", ["project_id"])
    op.create_index("ix_budget_records_proj_period", "budget_records", ["project_id", "period"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("entity_type", sa.String(length=30), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("actor", sa.String(length=100), nullable=False, server_default="system"),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_logs_project_id", "audit_logs", ["project_id"])
    op.create_index("ix_audit_logs_proj_created", "audit_logs", ["project_id", "created_at"])

    op.create_table(
        "project_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("snapshot_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("health", sa.String(length=20), nullable=False, server_default="green"),
        sa.Column("metrics_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("state_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_project_snapshots_project_id", "project_snapshots", ["project_id"])
    op.create_index("ix_project_snapshots_proj_date", "project_snapshots", ["project_id", "snapshot_date"])

    op.create_table(
        "data_quality_checks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("check_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pass"),
        sa.Column("score", sa.Float(), nullable=False, server_default="100.0"),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_data_quality_checks_project_id", "data_quality_checks", ["project_id"])
    op.create_index("ix_data_quality_proj_created", "data_quality_checks", ["project_id", "created_at"])

    op.create_table(
        "risk_thresholds",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("signal_type", sa.String(length=50), nullable=False),
        sa.Column("warning_threshold", sa.Float(), nullable=False),
        sa.Column("critical_threshold", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_risk_thresholds_project_id", "risk_thresholds", ["project_id"])
    op.create_index("ix_risk_thresholds_proj_cat_sig", "risk_thresholds", ["project_id", "category", "signal_type"], unique=True)

    op.create_table(
        "sync_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("data_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("data_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="running"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("items_synced", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("ix_sync_jobs_project_id", "sync_jobs", ["project_id"])
    op.create_index("ix_sync_jobs_data_source_id", "sync_jobs", ["data_source_id"])
    op.create_index("ix_sync_jobs_proj_started", "sync_jobs", ["project_id", "started_at"])

    op.create_table(
        "embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_embeddings_project_id", "embeddings", ["project_id"])
    op.create_index("ix_embeddings_source_id", "embeddings", ["source_id"])
    op.create_index("ix_embeddings_proj_source", "embeddings", ["project_id", "source_type", "source_id"])


def downgrade() -> None:
    op.drop_table("embeddings")
    op.drop_table("sync_jobs")
    op.drop_table("risk_thresholds")
    op.drop_table("data_quality_checks")
    op.drop_table("project_snapshots")
    op.drop_table("audit_logs")
    op.drop_table("budget_records")
    op.drop_table("outcomes")
    op.drop_table("actions")
    op.drop_table("recommendations")
    op.drop_table("evidence")
    op.drop_table("risk_signals")
    op.drop_table("risk_events")
    op.drop_table("team_members")
    op.drop_table("teams")
    op.drop_table("dependencies")
    op.drop_table("work_items")
    op.drop_table("milestones")
