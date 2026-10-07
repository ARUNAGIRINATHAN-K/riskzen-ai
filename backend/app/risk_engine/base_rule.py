import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Optional

from app.models.budget import BudgetRecord
from app.models.project import Project
from app.models.team import TeamMember
from app.models.work_item import Dependency, Milestone, WorkItem


@dataclass
class ProjectState:
    """In-memory snapshot of complete project data for ultra-fast rule evaluation."""

    project: Project
    work_items: list[WorkItem] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)
    budget_records: list[BudgetRecord] = field(default_factory=list)
    team_members: list[TeamMember] = field(default_factory=list)
    data_quality_score: float = 100.0
    today: date = field(default_factory=lambda: datetime.now(timezone.utc).date())


@dataclass
class EvidenceItem:
    """Evidence snippet supporting a detected risk signal."""

    source_type: str  # work_item, dependency, milestone, budget
    reference_label: str
    explanation: str
    reference_id: Optional[uuid.UUID] = None
    relevance_score: float = 1.0


@dataclass
class RiskSignal:
    """Deterministic telemetry signal emitted by a risk rule."""

    category: str  # schedule, dependency, scope, capacity, quality, budget, decision
    signal_type: str  # e.g., overdue_tasks, blocked_tasks
    severity: str  # low, medium, high, critical
    value: float
    threshold: float
    score: float  # normalized 0.0 to 1.0
    title: str
    description: str
    affected_milestone_id: Optional[uuid.UUID] = None
    details: dict[str, Any] = field(default_factory=dict)
    evidence_items: list[EvidenceItem] = field(default_factory=list)


class BaseRiskRule(ABC):
    """Abstract base class for all deterministic risk detection rules."""

    category: str = "general"
    signal_type: str = "base_signal"

    @abstractmethod
    def evaluate(self, state: ProjectState, thresholds: dict[str, float]) -> list[RiskSignal]:
        """Evaluate the project state against deterministic criteria and return emitted signals.

        Must be completely synchronous and pure (zero I/O, zero LLM calls).
        """
        pass
