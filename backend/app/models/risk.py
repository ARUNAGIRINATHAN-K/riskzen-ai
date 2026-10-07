import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class RiskEvent(Base, UUIDMixin, TimestampMixin):
    """Detected material or emerging risk event."""

    __tablename__ = "risk_events"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    affected_milestone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("milestones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # schedule, dependency, scope, capacity, quality, budget, decision
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    confidence: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high
    score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="new", nullable=False
    )  # new, active, mitigated, resolved, closed, dismissed
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    agent_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    agent_investigated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="risk_events")  # type: ignore # noqa: F821
    signals: Mapped[list["RiskSignal"]] = relationship("RiskSignal", back_populates="risk_event", cascade="all, delete-orphan", lazy="selectin")
    evidence_items: Mapped[list["Evidence"]] = relationship("Evidence", back_populates="risk_event", cascade="all, delete-orphan", lazy="selectin")
    history: Mapped[list["RiskHistory"]] = relationship("RiskHistory", back_populates="risk_event", cascade="all, delete-orphan", lazy="selectin")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="risk_event", cascade="all, delete-orphan", lazy="selectin")  # type: ignore # noqa: F821
    outcome: Mapped[Optional["Outcome"]] = relationship("Outcome", back_populates="risk_event", uselist=False, cascade="all, delete-orphan", lazy="selectin")  # type: ignore # noqa: F821

    __table_args__ = (
        Index("ix_risk_events_proj_stat_sev", "project_id", "status", "severity"),
        Index("ix_risk_events_detected_at", "detected_at"),
        Index("ix_risk_events_proj_cat", "project_id", "category"),
    )

    def __repr__(self) -> str:
        return f"<RiskEvent(id={self.id}, category='{self.category}', severity='{self.severity}', status='{self.status}')>"


class RiskSignal(Base, UUIDMixin):
    """Deterministic telemetry signal that contributed to a RiskEvent."""

    __tablename__ = "risk_signals"

    risk_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risk_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    signal_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. overdue_tasks, blocked_items
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    risk_event: Mapped["RiskEvent"] = relationship("RiskEvent", back_populates="signals")


class Evidence(Base, UUIDMixin):
    """Contextual evidence item supporting a risk event."""

    __tablename__ = "evidence"

    risk_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risk_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)  # work_item, dependency, milestone, budget, agent
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    reference_label: Mapped[str] = mapped_column(String(200), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    risk_event: Mapped["RiskEvent"] = relationship("RiskEvent", back_populates="evidence_items")


class RiskHistory(Base, UUIDMixin):
    """Historical timeline log tracking severity and score changes for a risk event."""

    __tablename__ = "risk_histories"

    risk_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("risk_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    risk_event: Mapped["RiskEvent"] = relationship("RiskEvent", back_populates="history")

    __table_args__ = (
        Index("ix_risk_histories_event_date", "risk_event_id", "recorded_at"),
    )
