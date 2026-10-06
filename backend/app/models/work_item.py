import uuid
from datetime import date, datetime, timezone
from typing import Any, Optional
from sqlalchemy import Date, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Milestone(Base, UUIDMixin):
    """Milestone entity representing key deliverable checkpoints."""

    __tablename__ = "milestones"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)  # open / closed
    completion_percent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="milestones")  # type: ignore # noqa: F821
    work_items: Mapped[list["WorkItem"]] = relationship("WorkItem", back_populates="milestone")

    def __repr__(self) -> str:
        return f"<Milestone(id={self.id}, title='{self.title}', target_date={self.target_date}, status='{self.status}')>"


class WorkItem(Base, UUIDMixin, TimestampMixin):
    """Normalized work item entity (Issue, Task, Bug, PR, Decision)."""

    __tablename__ = "work_items"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    milestone_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("milestones.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(30), default="github", nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="open", nullable=False)  # open, in_progress, done, closed
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    item_type: Mapped[str] = mapped_column(String(30), default="task", nullable=False)  # task, bug, feature, decision, pull_request
    assignee: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, index=True)
    labels: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cycle_time_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="work_items")  # type: ignore # noqa: F821
    milestone: Mapped[Optional["Milestone"]] = relationship("Milestone", back_populates="work_items")

    # Dependency relationships
    blocked_by_dependencies: Mapped[list["Dependency"]] = relationship(
        "Dependency",
        foreign_keys="Dependency.source_item_id",
        back_populates="source_item",
        cascade="all, delete-orphan",
    )
    blocking_dependencies: Mapped[list["Dependency"]] = relationship(
        "Dependency",
        foreign_keys="Dependency.target_item_id",
        back_populates="target_item",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_work_items_project_status", "project_id", "status"),
        Index("ix_work_items_project_priority", "project_id", "priority"),
    )

    def __repr__(self) -> str:
        return f"<WorkItem(id={self.id}, ext_id='{self.external_id}', title='{self.title[:30]}', status='{self.status}')>"


class Dependency(Base, UUIDMixin):
    """Dependency relationship between work items."""

    __tablename__ = "dependencies"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("work_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )  # The blocked item
    target_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("work_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )  # The prerequisite/blocker item
    dependency_type: Mapped[str] = mapped_column(String(30), default="blocks", nullable=False)  # blocks, depends_on, related
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, resolved
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="dependencies")  # type: ignore # noqa: F821
    source_item: Mapped["WorkItem"] = relationship("WorkItem", foreign_keys=[source_item_id], back_populates="blocked_by_dependencies")
    target_item: Mapped["WorkItem"] = relationship("WorkItem", foreign_keys=[target_item_id], back_populates="blocking_dependencies")

    __table_args__ = (
        Index("ix_dependencies_project_status", "project_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Dependency(id={self.id}, blocked={self.source_item_id}, blocker={self.target_item_id}, status='{self.status}')>"
