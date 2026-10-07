"""Risk history table for tracking risk event evolution

Revision ID: 003_risk_history
Revises: 002_core_data_foundation
Create Date: 2026-10-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "003_risk_history"
down_revision: Union[str, None] = "002_core_data_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "risk_histories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("risk_event_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("risk_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_risk_histories_risk_event_id", "risk_histories", ["risk_event_id"])
    op.create_index("ix_risk_histories_event_date", "risk_histories", ["risk_event_id", "recorded_at"])


def downgrade() -> None:
    op.drop_table("risk_histories")
