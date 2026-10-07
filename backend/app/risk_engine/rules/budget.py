"""Deterministic Risk Rules for Budget & Resource Consumption Risk Category."""
from typing import List

from app.models.risk import RiskCategory, RiskSeverity
from app.risk_engine.base_rule import BaseRiskRule, EvidenceItem, ProjectState, RiskSignal


class BudgetVarianceRule(BaseRiskRule):
    """Detects budget overruns or estimated vs actual effort variance."""

    rule_id = "BUDGET_VARIANCE_001"
    name = "Budget & Effort Variance Detection"
    category = RiskCategory.BUDGET

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        variance_threshold = self.get_threshold(state, "budget_variance_threshold", 0.20)  # 20% variance

        # 1. Project-level budget vs spent if metadata/project properties available
        project = state.project
        meta = project.settings or {}
        planned_budget = meta.get("planned_budget") or meta.get("budget")
        actual_spend = meta.get("actual_spend") or meta.get("current_spend")

        if planned_budget and actual_spend:
            try:
                planned = float(planned_budget)
                spend = float(actual_spend)
                if planned > 0:
                    variance = (spend - planned) / planned
                    if variance >= variance_threshold:
                        severity = RiskSeverity.CRITICAL if variance >= 0.40 else RiskSeverity.HIGH
                        signals.append(
                            RiskSignal(
                                rule_id=self.rule_id,
                                category=self.category,
                                signal_type="BUDGET_OVERRUN",
                                severity=severity,
                                confidence=0.90,
                                title=f"Budget Overrun ({variance:.1%} over budget)",
                                description=(
                                    f"Actual project spend (${spend:,.2f}) exceeds planned budget (${planned:,.2f}) "
                                    f"by {variance:.1%}, surpassing the {variance_threshold:.0%} threshold."
                                ),
                                score=min(1.0, 0.5 + variance),
                                raw_metrics={
                                    "planned_budget": planned,
                                    "actual_spend": spend,
                                    "variance": round(variance, 3),
                                    "threshold": variance_threshold,
                                },
                            )
                        )
            except (ValueError, TypeError):
                pass

        # 2. Story points / Estimated hours variance across work items
        total_estimated_points = 0.0
        completed_points = 0.0
        for item in state.work_items:
            pts = float(item.story_points or 0.0)
            total_estimated_points += pts
            if item.status.lower() in ("closed", "done", "completed"):
                completed_points += pts

        # Check for items with missing estimates if project relies on points
        items_with_pts = [item for item in state.work_items if item.story_points is not None]
        if len(state.work_items) >= 10 and len(items_with_pts) > 0:
            unestimated = len(state.work_items) - len(items_with_pts)
            unestimated_ratio = unestimated / len(state.work_items)
            if unestimated_ratio >= 0.40:
                signals.append(
                    RiskSignal(
                        rule_id=self.rule_id,
                        category=self.category,
                        signal_type="EFFORT_ESTIMATION_UNCERTAINTY",
                        severity=RiskSeverity.MEDIUM,
                        confidence=0.75,
                        title=f"High Estimation Uncertainty ({unestimated} unestimated tasks)",
                        description=(
                            f"{unestimated} out of {len(state.work_items)} work items ({unestimated_ratio:.1%}) "
                            f"lack story point estimates, introducing budget and capacity forecast uncertainty."
                        ),
                        score=min(1.0, 0.3 + unestimated_ratio),
                        raw_metrics={
                            "unestimated_items": unestimated,
                            "total_items": len(state.work_items),
                            "unestimated_ratio": round(unestimated_ratio, 3),
                        },
                    )
                )

        return signals


class BurnRateAccelerationRule(BaseRiskRule):
    """Detects unsustainable burn rate or point depletion velocity."""

    rule_id = "BUDGET_BURN_RATE_002"
    name = "Effort & Burn Rate Acceleration Detection"
    category = RiskCategory.BUDGET

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []

        # Compare milestone progress vs time elapsed
        now = state.evaluation_time
        for milestone in state.milestones:
            if not milestone.start_date or not milestone.due_date:
                continue

            s_date = milestone.start_date.replace(tzinfo=timezone.utc) if milestone.start_date.tzinfo is None else milestone.start_date
            d_date = milestone.due_date.replace(tzinfo=timezone.utc) if milestone.due_date.tzinfo is None else milestone.due_date

            total_days = (d_date - s_date).days
            if total_days <= 0:
                continue

            elapsed_days = (now - s_date).days
            if elapsed_days <= 0:
                continue

            time_elapsed_ratio = min(1.0, elapsed_days / total_days)

            m_items = state.items_by_milestone.get(str(milestone.id), [])
            if not m_items:
                continue

            completed_items = [
                i for i in m_items
                if i.status.lower() in ("closed", "done", "completed")
            ]
            completion_ratio = len(completed_items) / len(m_items)

            # If 70% time elapsed but < 30% items completed
            if time_elapsed_ratio >= 0.60 and (time_elapsed_ratio - completion_ratio) >= 0.35:
                gap = time_elapsed_ratio - completion_ratio
                severity = RiskSeverity.HIGH if gap >= 0.50 else RiskSeverity.MEDIUM
                signals.append(
                    RiskSignal(
                        rule_id=self.rule_id,
                        category=self.category,
                        signal_type="UNSUSTAINABLE_BURN_PACING",
                        severity=severity,
                        confidence=0.85,
                        title=f"Burn Pacing Gap in Milestone '{milestone.title}'",
                        description=(
                            f"Milestone is {time_elapsed_ratio:.0%} through its timeline, "
                            f"but only {completion_ratio:.0%} of work items ({len(completed_items)}/{len(m_items)}) are completed."
                        ),
                        score=min(1.0, 0.4 + gap),
                        affected_milestone_id=str(milestone.id),
                        raw_metrics={
                            "time_elapsed_ratio": round(time_elapsed_ratio, 3),
                            "completion_ratio": round(completion_ratio, 3),
                            "gap": round(gap, 3),
                        },
                    )
                )

        return signals
