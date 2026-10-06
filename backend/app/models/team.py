import uuid
from typing import Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Team(Base, UUIDMixin, TimestampMixin):
    """Team model grouping engineers working on a project."""

    __tablename__ = "teams"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="teams")  # type: ignore # noqa: F821
    members: Mapped[list["TeamMember"]] = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base, UUIDMixin, TimestampMixin):
    """Individual member of a project delivery team."""

    __tablename__ = "team_members"

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(100), default="engineer", nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    github_username: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)

    # Relationships
    team: Mapped["Team"] = relationship("Team", back_populates="members")
