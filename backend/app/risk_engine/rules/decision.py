"""Deterministic Risk Rules for Decision & Process Latency Risk Category."""
from datetime import timezone
from typing import List

from app.models.risk import RiskCategory, RiskSeverity
from app.risk_engine.base_rule import BaseRiskRule, EvidenceItem, ProjectState, RiskSignal


class LongRunningBlockersRule(BaseRiskRule):
    """Detects blocked work items languishing without resolution past threshold days."""

    rule_id = "DECISION_BLOCKER_AGE_001"
    name = "Long-Running Blocker & Impasse Detection"
    category = RiskCategory.DECISION

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        blocker_days_threshold = int(self.get_threshold(state, "blocker_staleness_days", 5))
        now = state.evaluation_time

        stalled_blockers = []
        for item in state.work_items:
            if item.status.lower() in ("closed", "done", "completed"):
                continue

            is_blocked = (
                item.status.lower() in ("blocked", "impediment", "waiting", "on hold", "hold")
                or "blocked" in (item.labels or [])
                or "decision-needed" in (item.labels or [])
            )

            if is_blocked:
                # Check how long it has been in this state (using updated_at or created_at)
                ref_time = item.updated_at or item.created_at
                if ref_time:
                    r_time = ref_time.replace(tzinfo=timezone.utc) if ref_time.tzinfo is None else ref_time
                    stalled_days = (now - r_time).days
                    if stalled_days >= blocker_days_threshold:
                        stalled_blockers.append((item, stalled_days))

        if stalled_blockers:
            severity = RiskSeverity.HIGH if len(stalled_blockers) >= 3 else RiskSeverity.MEDIUM
            signals.append(
                RiskSignal(
                    rule_id=self.rule_id,
                    category=self.category,
                    signal_type="PROTRACTED_BLOCKER",
                    severity=severity,
                    confidence=0.85,
                    title=f"Unresolved Blockers ({len(stalled_blockers)} items stalled > {blocker_days_threshold}d)",
                    description=(
                        f"{len(stalled_blockers)} work items have remained blocked or waiting on decisions "
                        f"for over {blocker_days_threshold} days without progress."
                    ),
                    score=min(1.0, 0.4 + (len(stalled_blockers) * 0.1)),
                    evidence=[
                        EvidenceItem(
                            source_type="work_item",
                            source_id=str(item.id),
                            description=f"Blocked task ({days}d): {item.title}",
                            metadata={"status": item.status, "days_stalled": days},
                        )
                        for item, days in stalled_blockers[:5]
                    ],
                    raw_metrics={
                        "stalled_blockers_count": len(stalled_blockers),
                        "threshold_days": blocker_days_threshold,
                    },
                )
            )

        return signals


class StalledPRReviewsRule(BaseRiskRule):
    """Detects pull requests / code reviews idling without resolution."""

    rule_id = "DECISION_PR_REVIEW_002"
    name = "Stalled Code Review / Pull Request Detection"
    category = RiskCategory.DECISION

    def evaluate(self, state: ProjectState) -> List[RiskSignal]:
        signals: List[RiskSignal] = []
        pr_staleness_threshold = int(self.get_threshold(state, "pr_review_sla_days", 4))
        now = state.evaluation_time

        stalled_prs = []
        for item in state.work_items:
            # Check for PR items (from GitHub connector or work items with PR type)
            is_pr = (
                (item.item_type or "").lower() in ("pull_request", "pr", "review")
                or "pr" in (item.labels or [])
            )
            if is_pr and item.status.lower() in ("open", "in_review", "review"):
                ref_time = item.created_at or item.updated_at
                if ref_time:
                    r_time = ref_time.replace(tzinfo=timezone.utc) if ref_time.tzinfo is None else ref_time
                    age_days = (now - r_time).days
                    if age_days >= pr_staleness_threshold:
                        stalled_prs.append((item, age_days))

        if stalled_prs:
            signals.append(
                RiskSignal(
                    rule_id=self.rule_id,
                    category=self.category,
                    signal_type="STALLED_CODE_REVIEW",
                    severity=RiskSeverity.MEDIUM,
                    confidence=0.80,
                    title=f"Stalled Pull Requests ({len(stalled_prs)} PRs awaiting review > {pr_staleness_threshold}d)",
                    description=(
                        f"{len(stalled_prs)} pull requests have remained open for code review "
                        f"longer than {pr_staleness_threshold} days, stalling team integration velocity."
                    ),
                    score=min(1.0, 0.35 + (len(stalled_prs) * 0.08)),
                    evidence=[
                        EvidenceItem(
                            source_type="work_item",
                            source_id=str(item.id),
                            description=f"Stalled PR ({days}d): {item.title}",
                            metadata={"days_open": days},
                        )
                        for item, days in stalled_prs[:5]
                    ],
                    raw_metrics={
                        "stalled_prs_count": len(stalled_prs),
                        "threshold_days": pr_staleness_threshold,
                    },
                )
            )

        return signals
