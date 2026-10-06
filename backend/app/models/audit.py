import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin


class AuditLog(Base, UUIDMixin):
    """Immutable audit trail of risk events, PM decisions, and system operations."""

    __tablename__ = "audit_logs"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # risk_detected, recommendation_approved, recommendation_dismissed, action_created, sync_completed
    entity_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # risk_event, recommendation, action, sync_job, data_source
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    actor: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="audit_logs")  # type: ignore # noqa: F821

    __table_args__ = (
        Index("ix_audit_logs_proj_created", "project_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(event='{self.event_type}', entity='{self.entity_type}', actor='{self.actor}')>"
