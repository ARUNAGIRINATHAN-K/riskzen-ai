from datetime import datetime, timedelta, timezone
from typing import Optional

from app.risk_engine.base_rule import BaseRiskRule, EvidenceItem, ProjectState, RiskSignal


class OverdueTasksRule(BaseRiskRule):
    """Detects open work items past their scheduled due date."""

    category = "schedule"
    signal_type = "overdue_tasks"

    def evaluate(self, state: ProjectState, thresholds: dict[str, dict[str, float]]) -> list[RiskSignal]:
        t = thresholds.get(self.signal_type, {"warning": 2.0, "critical": 5.0})
        warn_th, crit_th = t["warning"], t["critical"]

        overdue_items = [
            i for i in state.work_items
            if i.status in ["open", "in_progress"]
            and i.due_date is not None
            and i.due_date < state.today
        ]
        count = len(overdue_items)
        if count == 0:
            return []

        severity = "low"
        if count >= crit_th:
            severity = "critical"
        elif count >= warn_th:
            severity = "high" if count >= (warn_th + crit_th) / 2 else "medium"

        score = min(1.0, count / crit_th)

        evidence = [
            EvidenceItem(
                source_type="work_item",
                reference_id=item.id,
                reference_label=f"Task #{item.external_id or str(item.id)[:8]}",
                explanation=f"'{item.title}' was due on {item.due_date} ({(state.today - item.due_date).days} days overdue).",
            )
            for item in overdue_items[:5]
        ]

        return [
            RiskSignal(
                category=self.category,
                signal_type=self.signal_type,
                severity=severity,
                value=float(count),
                threshold=warn_th,
                score=score,
                title=f"{count} Overdue Work Items Detected",
                description=f"{count} open tasks have missed their scheduled due dates, accumulating schedule drag.",
                details={"overdue_count": count, "overdue_item_ids": [str(i.id) for i in overdue_items]},
                evidence_items=evidence,
            )
        ]


class MilestoneSlippageRule(BaseRiskRule):
    """Detects milestones at risk of slipping past their target date."""

    category = "schedule"
    signal_type = "milestone_slippage"

    def evaluate(self, state: ProjectState, thresholds: dict[str, dict[str, float]]) -> list[RiskSignal]:
        t = thresholds.get(self.signal_type, {"warning": 3.0, "critical": 7.0})
        warn_th, crit_th = t["warning"], t["critical"]
        signals: list[RiskSignal] = []

        for ms in state.milestones:
            if ms.status == "closed" or not ms.target_date:
                continue

            ms_items = [i for i in state.work_items if i.milestone_id == ms.id]
            total_items = len(ms_items)
            completed_items = sum(1 for i in ms_items if i.status in ["done", "closed"])
            open_items = total_items - completed_items

            days_remaining = (ms.target_date - state.today).days

            # Slip detection scenarios:
            # 1. Target date has already passed and open items remain
            if days_remaining < 0 and open_items > 0:
                slip_days = abs(days_remaining)
                severity = "critical" if slip_days >= crit_th else ("high" if slip_days >= warn_th else "medium")
                score = min(1.0, 0.7 + (slip_days / 10.0))
                signals.append(
                    RiskSignal(
                        category=self.category,
                        signal_type=self.signal_type,
                        severity=severity,
                        value=float(slip_days),
                        threshold=warn_th,
                        score=score,
                        title=f"Milestone '{ms.title}' Overdue by {slip_days} Days",
                        description=f"Milestone target date ({ms.target_date}) has passed with {open_items} open tasks remaining.",
                        affected_milestone_id=ms.id,
                        details={"milestone_id": str(ms.id), "slip_days": slip_days, "open_items": open_items},
                        evidence_items=[
                            EvidenceItem(
                                source_type="milestone",
                                reference_id=ms.id,
                                reference_label=f"Milestone: {ms.title}",
                                explanation=f"Target date was {ms.target_date}. Completion is currently at {ms.completion_percent}%.",
                            )
                        ],
                    )
                )

            # 2. Imminent slip: due in < 7 days with completion < 50%
            elif 0 <= days_remaining <= 7 and ms.completion_percent < 50.0 and total_items >= 3:
                projected_slip = 7 - days_remaining
                severity = "critical" if ms.completion_percent < 30.0 else "high"
                score = 0.85 if severity == "critical" else 0.65
                signals.append(
                    RiskSignal(
                        category=self.category,
                        signal_type=self.signal_type,
                        severity=severity,
                        value=float(projected_slip),
                        threshold=warn_th,
                        score=score,
                        title=f"Imminent Slippage on Milestone '{ms.title}'",
                        description=f"Only {days_remaining} days remaining until target date ({ms.target_date}) but milestone is only {ms.completion_percent}% complete ({open_items}/{total_items} open items).",
                        affected_milestone_id=ms.id,
                        details={"milestone_id": str(ms.id), "days_remaining": days_remaining, "completion_percent": ms.completion_percent},
                        evidence_items=[
                            EvidenceItem(
                                source_type="milestone",
                                reference_id=ms.id,
                                reference_label=f"Milestone: {ms.title}",
                                explanation=f"{open_items} of {total_items} work items remain open with only {days_remaining} days left.",
                            )
                        ],
                    )
                )

        return signals


class AgingWorkRule(BaseRiskRule):
    """Detects in-progress tasks that have become dormant with no updates in > 14 days."""

    category = "schedule"
    signal_type = "aging_work"

    def evaluate(self, state: ProjectState, thresholds: dict[str, dict[str, float]]) -> list[RiskSignal]:
        t = thresholds.get(self.signal_type, {"warning": 4.0, "critical": 8.0})
        warn_th, crit_th = t["warning"], t["critical"]

        stale_cutoff = datetime.now(timezone.utc) - timedelta(days=14)
        aging_items = [
            i for i in state.work_items
            if i.status in ["in_progress", "open"]
            and i.updated_at < stale_cutoff
        ]
        count = len(aging_items)
        if count == 0:
            return []

        severity = "low"
        if count >= crit_th:
            severity = "critical"
        elif count >= warn_th:
            severity = "high" if count >= (warn_th + crit_th) / 2 else "medium"

        score = min(1.0, count / crit_th)

        return [
            RiskSignal(
                category=self.category,
                signal_type=self.signal_type,
                severity=severity,
                value=float(count),
                threshold=warn_th,
                score=score,
                title=f"{count} Aging / Dormant Work Items",
                description=f"{count} work items have had zero activity or status updates for over 14 days.",
                details={"aging_count": count, "item_ids": [str(i.id) for i in aging_items[:10]]},
                evidence_items=[
                    EvidenceItem(
                        source_type="work_item",
                        reference_id=item.id,
                        reference_label=f"Task #{item.external_id or str(item.id)[:8]}",
                        explanation=f"'{item.title}' has had no updates since {item.updated_at.strftime('%Y-%m-%d')}.",
                    )
                    for item in aging_items[:4]
                ],
            )
        ]
