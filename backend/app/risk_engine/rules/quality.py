"""Deterministic Risk Rules for Quality Risk Category."""
from datetime import timezone
from typing import List

from app.models.risk import RiskCategory, RiskSeverity
from app.risk_engine.base_rule import BaseRiskRule, EvidenceItem, ProjectState, RiskSignal


class DefectGrowthRule(BaseRiskRule):
    """Detects defect growth and bug-to-feature ratio spikes."""

    rule_id = "QUALITY_DEFECT_GROWTH_001"
    name = "Defect Inflow vs Resolution Detection"
    category = RiskCategory.QUALITY

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        max_defect_ratio = self.get_threshold(state, "defect_ratio_threshold", 0.30)  # 30% of all items are bugs

        bug_items = [
            item for item in state.work_items
            if (item.item_type or "").lower() in ("bug", "defect", "incident")
            or "bug" in (item.labels or [])
        ]

        if not bug_items:
            return signals

        open_bugs = [
            b for b in bug_items
            if b.status.lower() not in ("closed", "done", "completed", "resolved")
        ]

        total_open = len([
            item for item in state.work_items
            if item.status.lower() not in ("closed", "done", "completed")
        ])

        if total_open > 0:
            defect_ratio = len(open_bugs) / total_open
            if defect_ratio >= max_defect_ratio and len(open_bugs) >= 3:
                severity = RiskSeverity.HIGH if defect_ratio >= 0.50 else RiskSeverity.MEDIUM
                signals.append(
                    RiskSignal(
                        rule_id=self.rule_id,
                        category=self.category,
                        signal_type="HIGH_DEFECT_RATIO",
                        severity=severity,
                        confidence=0.85,
                        title=f"High Defect Density ({len(open_bugs)} open bugs, {defect_ratio:.1%} of WIP)",
                        description=(
                            f"Open defects account for {defect_ratio:.1%} of active work items "
                            f"({len(open_bugs)} open defects out of {total_open} open items), "
                            f"exceeding quality threshold of {max_defect_ratio:.0%}."
                        ),
                        score=min(1.0, 0.4 + defect_ratio),
                        evidence=[
                            EvidenceItem(
                                source_type="work_item",
                                source_id=str(item.id),
                                description=f"Open defect: {item.title} [{item.priority or 'Normal'}]",
                                metadata={"priority": item.priority, "status": item.status},
                            )
                            for item in open_bugs[:5]
                        ],
                        raw_metrics={
                            "open_bugs_count": len(open_bugs),
                            "total_open_items": total_open,
                            "defect_ratio": round(defect_ratio, 3),
                            "threshold": max_defect_ratio,
                        },
                    )
                )

        return signals


class CriticalDefectDebtRule(BaseRiskRule):
    """Detects critical/high severity defects remaining unresolved past SLA days."""

    rule_id = "QUALITY_CRITICAL_DEBT_002"
    name = "Critical Defect Debt Detection"
    category = RiskCategory.QUALITY

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        critical_bug_sla_days = int(self.get_threshold(state, "critical_bug_sla_days", 7))
        now = state.evaluation_time

        critical_bugs = []
        for item in state.work_items:
            if item.status.lower() in ("closed", "done", "completed", "resolved"):
                continue

            is_bug = (
                (item.item_type or "").lower() in ("bug", "defect", "incident")
                or "bug" in (item.labels or [])
            )
            is_critical = (item.priority or "").lower() in ("critical", "urgent", "high")

            if is_bug and is_critical:
                if item.created_at:
                    c_at = item.created_at.replace(tzinfo=timezone.utc) if item.created_at.tzinfo is None else item.created_at
                    age_days = (now - c_at).days
                    if age_days >= critical_bug_sla_days:
                        critical_bugs.append((item, age_days))

        if critical_bugs:
            severity = RiskSeverity.CRITICAL if len(critical_bugs) >= 3 else RiskSeverity.HIGH
            signals.append(
                RiskSignal(
                    rule_id=self.rule_id,
                    category=self.category,
                    signal_type="CRITICAL_DEFECT_DEBT",
                    severity=severity,
                    confidence=0.90,
                    title=f"Critical Defect Debt ({len(critical_bugs)} high-severity bugs past SLA)",
                    description=(
                        f"{len(critical_bugs)} critical/high-severity defects have remained open longer than "
                        f"the {critical_bug_sla_days}-day SLA threshold without resolution."
                    ),
                    score=min(1.0, 0.6 + (len(critical_bugs) * 0.1)),
                    evidence=[
                        EvidenceItem(
                            source_type="work_item",
                            source_id=str(item.id),
                            description=f"Critical bug ({age_days}d open): {item.title}",
                            metadata={"age_days": age_days, "priority": item.priority},
                        )
                        for item, age_days in critical_bugs[:5]
                    ],
                    raw_metrics={
                        "critical_bugs_past_sla": len(critical_bugs),
                        "sla_days": critical_bug_sla_days,
                    },
                )
            )

        return signals


class ReopenedIssuesRule(BaseRiskRule):
    """Detects high rate of reopened or reworked tasks/issues."""

    rule_id = "QUALITY_REOPENED_003"
    name = "Reopened Issues & Rework Detection"
    category = RiskCategory.QUALITY

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []

        reopened_items = [
            item for item in state.work_items
            if "reopened" in (item.labels or [])
            or item.status.lower() in ("reopened", "re-opened")
        ]

        if len(reopened_items) >= 2:
            severity = RiskSeverity.HIGH if len(reopened_items) >= 4 else RiskSeverity.MEDIUM
            signals.append(
                RiskSignal(
                    rule_id=self.rule_id,
                    category=self.category,
                    signal_type="HIGH_REWORK_RATE",
                    severity=severity,
                    confidence=0.80,
                    title=f"High Rework Rate ({len(reopened_items)} reopened issues)",
                    description=(
                        f"{len(reopened_items)} work items have been reopened after initial completion, "
                        f"indicating testing regressions or incomplete initial verification."
                    ),
                    score=min(1.0, 0.4 + (len(reopened_items) * 0.1)),
                    evidence=[
                        EvidenceItem(
                            source_type="work_item",
                            source_id=str(item.id),
                            description=f"Reopened item: {item.title}",
                            metadata={"status": item.status, "labels": item.labels},
                        )
                        for item in reopened_items[:5]
                    ],
                    raw_metrics={"reopened_count": len(reopened_items)},
                )
            )

        return signals
