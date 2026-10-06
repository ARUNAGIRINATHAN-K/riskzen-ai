import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import UUIDMixin


class DataQualityCheck(Base, UUIDMixin):
    """Result of an automated data-quality assessment for a project."""

    __tablename__ = "data_quality_checks"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    check_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # missing_due_dates, stale_items, missing_target_dates, unresolved_deps, budget_coverage
    status: Mapped[str] = mapped_column(String(20), default="pass", nullable=False)  # pass, warn, fail
    score: Mapped[float] = mapped_column(Float, default=100.0, nullable=False)  # 0.0 - 100.0
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="data_quality_checks")  # type: ignore # noqa: F821

    __table_args__ = (
        Index("ix_data_quality_proj_created", "project_id", "created_at"),
    )
