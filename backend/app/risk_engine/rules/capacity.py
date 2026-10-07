"""Deterministic Risk Rules for Capacity Risk Category."""
from collections import defaultdict
from typing import Dict, List

from app.models.risk import RiskCategory, RiskSeverity
from app.risk_engine.base_rule import BaseRiskRule, EvidenceItem, ProjectState, RiskSignal


class WorkloadConcentrationRule(BaseRiskRule):
    """Detects single-person dependencies where work items or story points are heavily concentrated."""

    rule_id = "CAPACITY_CONCENTRATION_001"
    name = "Workload Concentration Detection"
    category = RiskCategory.CAPACITY

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        concentration_threshold = self.get_threshold(state, "capacity_concentration_ratio", 0.40)  # 40% of WIP

        open_items = [
            item for item in state.work_items
            if item.status.lower() not in ("closed", "done", "completed")
        ]

        if len(open_items) < 4:
            return signals

        # Count by assignee
        assignee_counts: Dict[str, List] = defaultdict(list)
        unassigned_count = 0

        for item in open_items:
            if item.assignee_id:
                assignee_counts[str(item.assignee_id)].append(item)
            else:
                unassigned_count += 1

        total_open = len(open_items)

        for assignee_id, items in assignee_counts.items():
            ratio = len(items) / total_open
            if ratio >= concentration_threshold:
                # Find member name if available
                member_name = assignee_id
                for m in state.members:
                    if str(m.id) == assignee_id or str(m.user_id) == assignee_id:
                        member_name = f"Member ({m.role or assignee_id})"
                        break

                severity = RiskSeverity.HIGH if ratio >= 0.60 else RiskSeverity.MEDIUM
                signals.append(
                    RiskSignal(
                        rule_id=self.rule_id,
                        category=self.category,
                        signal_type="WORKLOAD_CONCENTRATION",
                        severity=severity,
                        confidence=0.85,
                        title=f"High Workload Concentration on {member_name}",
                        description=(
                            f"{len(items)} out of {total_open} active work items ({ratio:.1%}) "
                            f"are assigned to a single team member, exceeding the {concentration_threshold:.0%} threshold."
                        ),
                        score=min(1.0, 0.4 + ratio),
                        evidence=[
                            EvidenceItem(
                                source_type="work_item",
                                source_id=str(item.id),
                                description=f"Assigned task: {item.title} [{item.status}]",
                                metadata={"assignee_id": assignee_id, "priority": item.priority},
                            )
                            for item in items[:5]
                        ],
                        raw_metrics={
                            "assignee_id": assignee_id,
                            "assigned_items_count": len(items),
                            "total_open_items": total_open,
                            "concentration_ratio": round(ratio, 3),
                            "threshold": concentration_threshold,
                        },
                    )
                )

        return signals


class ExcessiveWIPRule(BaseRiskRule):
    """Detects excessive work-in-progress (WIP) that threatens team delivery capacity."""

    rule_id = "CAPACITY_WIP_002"
    name = "Excessive Work-in-Progress (WIP) Detection"
    category = RiskCategory.CAPACITY

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        max_wip_per_member = self.get_threshold(state, "max_wip_per_member", 5.0)

        in_progress_items = [
            item for item in state.work_items
            if item.status.lower() in ("in_progress", "in progress", "doing", "active")
        ]

        active_members_count = len(state.members) or 1
        avg_wip = len(in_progress_items) / active_members_count

        if len(in_progress_items) >= 6 and avg_wip > max_wip_per_member:
            severity = RiskSeverity.HIGH if avg_wip >= max_wip_per_member * 1.5 else RiskSeverity.MEDIUM
            signals.append(
                RiskSignal(
                    rule_id=self.rule_id,
                    category=self.category,
                    signal_type="EXCESSIVE_WIP",
                    severity=severity,
                    confidence=0.80,
                    title=f"Excessive Work-in-Progress ({len(in_progress_items)} concurrent tasks)",
                    description=(
                        f"Current WIP is {avg_wip:.1f} tasks per active member "
                        f"({len(in_progress_items)} tasks across {active_members_count} members), "
                        f"exceeding recommended threshold of {max_wip_per_member:.1f} tasks/person."
                    ),
                    score=min(1.0, 0.4 + (avg_wip / (max_wip_per_member * 2))),
                    evidence=[
                        EvidenceItem(
                            source_type="work_item",
                            source_id=str(item.id),
                            description=f"In-progress item: {item.title}",
                            metadata={"assignee_id": str(item.assignee_id) if item.assignee_id else None},
                        )
                        for item in in_progress_items[:5]
                    ],
                    raw_metrics={
                        "in_progress_count": len(in_progress_items),
                        "team_size": active_members_count,
                        "avg_wip_per_member": round(avg_wip, 2),
                        "threshold": max_wip_per_member,
                    },
                )
            )

        return signals


class SingleOwnerBottleneckRule(BaseRiskRule):
    """Detects critical-path or blocking items concentrated on a single individual."""

    rule_id = "CAPACITY_BOTTLENECK_003"
    name = "Single Owner Bottleneck Detection"
    category = RiskCategory.CAPACITY

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []

        # Find items that are high priority or blocking other items
        high_priority_items = [
            item for item in state.work_items
            if item.status.lower() not in ("closed", "done", "completed")
            and (item.priority or "").lower() in ("critical", "urgent", "high")
            and item.assignee_id
        ]

        if len(high_priority_items) < 3:
            return signals

        # Count high priority items by assignee
        assignee_critical: Dict[str, List] = defaultdict(list)
        for item in high_priority_items:
            assignee_critical[str(item.assignee_id)].append(item)

        for assignee_id, items in assignee_critical.items():
            if len(items) >= 3:
                signals.append(
                    RiskSignal(
                        rule_id=self.rule_id,
                        category=self.category,
                        signal_type="KEY_PERSON_BOTTLENECK",
                        severity=RiskSeverity.HIGH if len(items) >= 5 else RiskSeverity.MEDIUM,
                        confidence=0.80,
                        title=f"Key Person Bottleneck ({len(items)} high-priority tasks on single owner)",
                        description=(
                            f"One team member is the sole owner of {len(items)} high/critical priority items. "
                            f"Any delay with this owner creates a single point of failure for delivery."
                        ),
                        score=min(1.0, 0.4 + (len(items) * 0.1)),
                        evidence=[
                            EvidenceItem(
                                source_type="work_item",
                                source_id=str(item.id),
                                description=f"Critical item: {item.title} [{item.priority}]",
                                metadata={"assignee_id": assignee_id, "priority": item.priority},
                            )
                            for item in items[:5]
                        ],
                        raw_metrics={
                            "assignee_id": assignee_id,
                            "critical_items_count": len(items),
                        },
                    )
                )

        return signals
