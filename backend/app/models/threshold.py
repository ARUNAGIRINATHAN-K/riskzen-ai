import uuid
from sqlalchemy import Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class RiskThreshold(Base, UUIDMixin, TimestampMixin):
    """Configurable risk signal threshold parameters per project."""

    __tablename__ = "risk_thresholds"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    warning_threshold: Mapped[float] = mapped_column(Float, nullable=False)
    critical_threshold: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="thresholds")  # type: ignore # noqa: F821

    __table_args__ = (
        Index("ix_risk_thresholds_proj_cat_sig", "project_id", "category", "signal_type", unique=True),
    )
