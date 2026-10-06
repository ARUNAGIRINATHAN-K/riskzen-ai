import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.audit import AuditLog
    from app.models.budget import BudgetRecord
    from app.models.data_quality import DataQualityCheck
    from app.models.embedding import Embedding
    from app.models.recommendation import Action
    from app.models.risk import RiskEvent
    from app.models.snapshot import ProjectSnapshot
    from app.models.sync import SyncJob
    from app.models.team import Team
    from app.models.threshold import RiskThreshold
    from app.models.work_item import Dependency, Milestone, WorkItem


class Project(Base, UUIDMixin, TimestampMixin):
    """Project entity representing a monitored software project."""

    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    project_type: Mapped[str] = mapped_column(String(50), default="software", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, paused, archived
    health: Mapped[str] = mapped_column(String(20), default="green", nullable=False)  # green, yellow, orange, red

    # Relationships
    data_sources: Mapped[list["DataSource"]] = relationship(
        "DataSource",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    work_items: Mapped[list["WorkItem"]] = relationship(
        "WorkItem",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    milestones: Mapped[list["Milestone"]] = relationship(
        "Milestone",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    dependencies: Mapped[list["Dependency"]] = relationship(
        "Dependency",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    teams: Mapped[list["Team"]] = relationship(
        "Team",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    risk_events: Mapped[list["RiskEvent"]] = relationship(
        "RiskEvent",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    actions: Mapped[list["Action"]] = relationship(
        "Action",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    budget_records: Mapped[list["BudgetRecord"]] = relationship(
        "BudgetRecord",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    snapshots: Mapped[list["ProjectSnapshot"]] = relationship(
        "ProjectSnapshot",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    data_quality_checks: Mapped[list["DataQualityCheck"]] = relationship(
        "DataQualityCheck",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    thresholds: Mapped[list["RiskThreshold"]] = relationship(
        "RiskThreshold",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sync_jobs: Mapped[list["SyncJob"]] = relationship(
        "SyncJob",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_projects_status", "status"),
        Index("ix_projects_health", "health"),
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', health='{self.health}', status='{self.status}')>"


class DataSource(Base, UUIDMixin):
    """Data source connection associated with a project (e.g., GitHub, CSV)."""

    __tablename__ = "data_sources"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)  # github, csv_budget
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="connected", nullable=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="data_sources")
    sync_jobs: Mapped[list["SyncJob"]] = relationship(
        "SyncJob",
        back_populates="data_source",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_data_sources_source_type", "source_type"),
    )

    def __repr__(self) -> str:
        return f"<DataSource(id={self.id}, type='{self.source_type}', status='{self.status}')>"
