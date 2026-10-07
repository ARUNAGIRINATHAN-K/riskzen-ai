from collections import defaultdict
from app.risk_engine.base_rule import BaseRiskRule, EvidenceItem, ProjectState, RiskSignal


class BlockedTasksRule(BaseRiskRule):
    """Detects open work items actively blocked by unfinished prerequisite tasks."""

    category = "dependency"
    signal_type = "blocked_tasks"

    def evaluate(self, state: ProjectState, thresholds: dict[str, dict[str, float]]) -> list[RiskSignal]:
        t = thresholds.get(self.signal_type, {"warning": 2.0, "critical": 4.0})
        warn_th, crit_th = t["warning"], t["critical"]

        active_deps = [d for d in state.dependencies if d.status == "active"]
        blocked_item_ids = set(d.source_item_id for d in active_deps)

        items_map = {i.id: i for i in state.work_items}
        truly_blocked = [
            items_map[bid] for bid in blocked_item_ids
            if bid in items_map and items_map[bid].status in ["open", "in_progress"]
        ]

        count = len(truly_blocked)
        if count == 0:
            return []

        severity = "low"
        if count >= crit_th:
            severity = "critical"
        elif count >= warn_th:
            severity = "high" if count >= (warn_th + crit_th) / 2 else "medium"

        score = min(1.0, count / crit_th)

        evidence = []
        for d in active_deps[:6]:
            blocked_item = items_map.get(d.source_item_id)
            blocker_item = items_map.get(d.target_item_id)
            if blocked_item and blocker_item:
                evidence.append(
                    EvidenceItem(
                        source_type="dependency",
                        reference_id=d.id,
                        reference_label=f"Blocker: Task #{blocker_item.external_id or str(blocker_item.id)[:6]}",
                        explanation=f"'{blocked_item.title}' is currently blocked by '{blocker_item.title}' (status: {blocker_item.status}).",
                    )
                )

        return [
            RiskSignal(
                category=self.category,
                signal_type=self.signal_type,
                severity=severity,
                value=float(count),
                threshold=warn_th,
                score=score,
                title=f"{count} Blocked Work Items on Delivery Path",
                description=f"{count} active work items are currently stalled waiting on upstream prerequisites.",
                details={"blocked_count": count, "blocked_ids": [str(i.id) for i in truly_blocked]},
                evidence_items=evidence,
            )
        ]


class OverdueUpstreamDependenciesRule(BaseRiskRule):
    """Detects prerequisite blocker tasks that are overdue, causing cascading delivery delays."""

    category = "dependency"
    signal_type = "overdue_upstream_dependencies"

    def evaluate(self, state: ProjectState, thresholds: dict[str, dict[str, float]]) -> list[RiskSignal]:
        t = thresholds.get(self.signal_type, {"warning": 1.0, "critical": 3.0})
        warn_th, crit_th = t["warning"], t["critical"]

        items_map = {i.id: i for i in state.work_items}
        active_deps = [d for d in state.dependencies if d.status == "active"]

        overdue_blockers = []
        for dep in active_deps:
            blocker = items_map.get(dep.target_item_id)
            blocked = items_map.get(dep.source_item_id)
            if blocker and blocked and blocker.status in ["open", "in_progress"]:
                if blocker.due_date and blocker.due_date < state.today:
                    overdue_blockers.append((blocker, blocked))

        count = len(overdue_blockers)
        if count == 0:
            return []

        severity = "critical" if count >= crit_th else ("high" if count >= warn_th else "medium")
        score = min(1.0, count / crit_th)

        evidence = [
            EvidenceItem(
                source_type="dependency",
                reference_id=blocker.id,
                reference_label=f"Overdue Blocker #{blocker.external_id or str(blocker.id)[:6]}",
                explanation=f"Blocker '{blocker.title}' is overdue (due: {blocker.due_date}) while blocking '{blocked.title}'.",
            )
            for blocker, blocked in overdue_blockers[:5]
        ]

        return [
            RiskSignal(
                category=self.category,
                signal_type=self.signal_type,
                severity=severity,
                value=float(count),
                threshold=warn_th,
                score=score,
                title=f"{count} Overdue Upstream Dependency Blockers",
                description=f"{count} critical blocker tasks are past their due dates, causing cascading blockages across downstream milestones.",
                details={"overdue_blockers_count": count},
                evidence_items=evidence,
            )
        ]


class DependencyConcentrationRule(BaseRiskRule):
    """Detects single points of failure where 1 work item blocks multiple downstream items."""

    category = "dependency"
    signal_type = "dependency_concentration"

    def evaluate(self, state: ProjectState, thresholds: dict[str, dict[str, float]]) -> list[RiskSignal]:
        t = thresholds.get(self.signal_type, {"warning": 3.0, "critical": 5.0})
        warn_th, crit_th = t["warning"], t["critical"]

        items_map = {i.id: i for i in state.work_items}
        active_deps = [d for d in state.dependencies if d.status == "active"]

        # Count dependents per blocker target item
        blocker_counts: dict[uuid.UUID, list[WorkItem]] = defaultdict(list)
        for dep in active_deps:
            blocked = items_map.get(dep.source_item_id)
            if blocked and blocked.status in ["open", "in_progress"]:
                blocker_counts[dep.target_item_id].append(blocked)

        signals: list[RiskSignal] = []
        for blocker_id, dependents in blocker_counts.items():
            dep_count = len(dependents)
            if dep_count >= warn_th:
                blocker = items_map.get(blocker_id)
                blocker_title = blocker.title if blocker else "Unknown Task"
                severity = "critical" if dep_count >= crit_th else "high"
                score = min(1.0, dep_count / crit_th)

                signals.append(
                    RiskSignal(
                        category=self.category,
                        signal_type=self.signal_type,
                        severity=severity,
                        value=float(dep_count),
                        threshold=warn_th,
                        score=score,
                        title=f"High Dependency Bottleneck on Task '{blocker_title[:40]}'",
                        description=f"Single work item '{blocker_title}' directly blocks {dep_count} downstream deliverables.",
                        details={"blocker_id": str(blocker_id), "dependent_count": dep_count},
                        evidence_items=[
                            EvidenceItem(
                                source_type="work_item",
                                reference_id=blocker_id,
                                reference_label=f"Bottleneck Task #{blocker.external_id if blocker else str(blocker_id)[:6]}",
                                explanation=f"This task is blocking {dep_count} deliverables: {', '.join([d.title[:30] for d in dependents[:3]])}...",
                            )
                        ],
                    )
                )

        return signals
