import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin


class ProjectSnapshot(Base, UUIDMixin):
    """Point-in-time snapshot of project health, work items, and metrics."""

    __tablename__ = "project_snapshots"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    snapshot_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    health: Mapped[str] = mapped_column(String(20), default="green", nullable=False)
    metrics_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    state_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="snapshots")  # type: ignore # noqa: F821

    __table_args__ = (
        Index("ix_project_snapshots_proj_date", "project_id", "snapshot_date"),
    )
