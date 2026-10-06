import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class BudgetRecord(Base, UUIDMixin, TimestampMixin):
    """Budget financial tracking line item ingested from CSV or manual entry."""

    __tablename__ = "budget_records"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    period: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "2026-10", "2026-Q4"
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "Engineering", "Contractors", "Cloud Infra"
    planned_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    variance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # actual - planned
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    source_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="budget_records")  # type: ignore # noqa: F821

    __table_args__ = (
        Index("ix_budget_records_proj_period", "project_id", "period"),
    )

    def __repr__(self) -> str:
        return f"<BudgetRecord(period='{self.period}', category='{self.category}', planned={self.planned_amount}, actual={self.actual_amount})>"
