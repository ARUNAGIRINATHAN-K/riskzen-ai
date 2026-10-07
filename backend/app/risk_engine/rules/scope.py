"""Deterministic Risk Rules for Scope Risk Category."""
from datetime import datetime, timezone
from typing import List

from app.models.risk import RiskCategory, RiskSeverity
from app.risk_engine.base_rule import BaseRiskRule, EvidenceItem, ProjectState, RiskSignal


class ScopeGrowthRule(BaseRiskRule):
    """Detects rapid growth in work items or story points after baseline/milestone start."""

    rule_id = "SCOPE_GROWTH_001"
    name = "Scope Growth & Creep Detection"
    category = RiskCategory.SCOPE

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        growth_threshold = self.get_threshold(state, "scope_growth_rate", 0.20)  # 20% growth
        now = state.evaluation_time

        # 1. Milestone-level scope growth
        for milestone in state.milestones:
            m_items = state.items_by_milestone.get(str(milestone.id), [])
            if not m_items:
                continue

            # Check items added after milestone start date if available
            start_date = milestone.start_date
            if start_date:
                if start_date.tzinfo is None:
                    start_date = start_date.replace(tzinfo=timezone.utc)
                
                initial_items = [
                    item for item in m_items
                    if item.created_at and (
                        item.created_at.replace(tzinfo=timezone.utc) if item.created_at.tzinfo is None else item.created_at
                    ) <= start_date
                ]
                added_items = [
                    item for item in m_items
                    if item.created_at and (
                        item.created_at.replace(tzinfo=timezone.utc) if item.created_at.tzinfo is None else item.created_at
                    ) > start_date
                ]

                if initial_items:
                    growth_ratio = len(added_items) / len(initial_items)
                    if growth_ratio >= growth_threshold:
                        severity = RiskSeverity.HIGH if growth_ratio >= 0.40 else RiskSeverity.MEDIUM
                        signals.append(
                            RiskSignal(
                                rule_id=self.rule_id,
                                category=self.category,
                                signal_type="MILESTONE_SCOPE_CREEP",
                                severity=severity,
                                confidence=0.85,
                                title=f"Scope Creep in Milestone '{milestone.title}'",
                                description=(
                                    f"Milestone '{milestone.title}' has expanded by {growth_ratio:.1%} "
                                    f"({len(added_items)} items added after start date vs {len(initial_items)} initial items), "
                                    f"exceeding the {growth_threshold:.0%} threshold."
                                ),
                                score=min(1.0, 0.4 + growth_ratio),
                                evidence=[
                                    EvidenceItem(
                                        source_type="work_item",
                                        source_id=str(item.id),
                                        description=f"Added item: {item.title} ({item.item_type or 'task'})",
                                        metadata={"created_at": item.created_at.isoformat() if item.created_at else None},
                                    )
                                    for item in added_items[:5]
                                ],
                                affected_milestone_id=str(milestone.id),
                                raw_metrics={
                                    "initial_items_count": len(initial_items),
                                    "added_items_count": len(added_items),
                                    "growth_ratio": round(growth_ratio, 3),
                                    "threshold": growth_threshold,
                                },
                            )
                        )

        # 2. Overall project scope growth in last 14 days
        total_items = len(state.work_items)
        if total_items >= 10:
            recent_added = [
                item for item in state.work_items
                if item.created_at and (now - (
                    item.created_at.replace(tzinfo=timezone.utc) if item.created_at.tzinfo is None else item.created_at
                )).days <= 14
            ]
            recent_ratio = len(recent_added) / total_items
            if recent_ratio >= 0.35:  # 35% of all items created in last 14 days
                signals.append(
                    RiskSignal(
                        rule_id=self.rule_id,
                        category=self.category,
                        signal_type="RAPID_PROJECT_SCOPE_EXPANSION",
                        severity=RiskSeverity.MEDIUM,
                        confidence=0.75,
                        title="Rapid Project Scope Expansion",
                        description=(
                            f"{len(recent_added)} new work items created in the past 14 days, "
                            f"representing {recent_ratio:.1%} of total project backlog."
                        ),
                        score=min(1.0, 0.3 + recent_ratio),
                        evidence=[
                            EvidenceItem(
                                source_type="work_item",
                                source_id=str(item.id),
                                description=f"Recently created: {item.title}",
                                metadata={"created_at": item.created_at.isoformat() if item.created_at else None},
                            )
                            for item in recent_added[:5]
                        ],
                        raw_metrics={
                            "recent_items_14d": len(recent_added),
                            "total_items": total_items,
                            "recent_ratio": round(recent_ratio, 3),
                        },
                    )
                )

        return signals


class RequirementChurnRule(BaseRiskRule):
    """Detects frequent modifications or churn in work items."""

    rule_id = "SCOPE_CHURN_002"
    name = "Requirement Churn Detection"
    category = RiskCategory.SCOPE

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        churn_threshold = self.get_threshold(state, "requirement_churn_rate", 0.25)
        now = state.evaluation_time

        # Detect items updated frequently (e.g. updated_at is very recent and different from created_at)
        churned_items = []
        for item in state.work_items:
            if item.status.lower() in ("closed", "done", "completed"):
                continue
            if item.created_at and item.updated_at:
                c_at = item.created_at.replace(tzinfo=timezone.utc) if item.created_at.tzinfo is None else item.created_at
                u_at = item.updated_at.replace(tzinfo=timezone.utc) if item.updated_at.tzinfo is None else item.updated_at
                # If item was modified more than 3 days after creation, and updated in last 7 days
                if (u_at - c_at).days >= 3 and (now - u_at).days <= 7:
                    churned_items.append(item)

        if state.work_items:
            churn_ratio = len(churned_items) / len(state.work_items)
            if churn_ratio >= churn_threshold and len(churned_items) >= 3:
                severity = RiskSeverity.HIGH if churn_ratio >= 0.50 else RiskSeverity.MEDIUM
                signals.append(
                    RiskSignal(
                        rule_id=self.rule_id,
                        category=self.category,
                        signal_type="HIGH_REQUIREMENT_CHURN",
                        severity=severity,
                        confidence=0.70,
                        title=f"High Requirement Churn ({len(churned_items)} items modified)",
                        description=(
                            f"{len(churned_items)} active work items ({churn_ratio:.1%}) have undergone recent updates "
                            f"and modifications, indicating fluid or unstable requirements."
                        ),
                        score=min(1.0, 0.3 + churn_ratio),
                        evidence=[
                            EvidenceItem(
                                source_type="work_item",
                                source_id=str(item.id),
                                description=f"Modified item: {item.title}",
                                metadata={"updated_at": item.updated_at.isoformat() if item.updated_at else None},
                            )
                            for item in churned_items[:5]
                        ],
                        raw_metrics={
                            "churned_items_count": len(churned_items),
                            "total_items": len(state.work_items),
                            "churn_ratio": round(churn_ratio, 3),
                            "threshold": churn_threshold,
                        },
                    )
                )

        return signals
