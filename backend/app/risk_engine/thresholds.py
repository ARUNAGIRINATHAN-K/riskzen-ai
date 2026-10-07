from typing import Any

# Default risk thresholds across all 7 categories
DEFAULT_THRESHOLDS: dict[str, dict[str, Any]] = {
    # 1. Schedule
    "overdue_tasks": {
        "category": "schedule",
        "signal_type": "overdue_tasks",
        "warning_threshold": 2.0,
        "critical_threshold": 5.0,
        "unit": "count",
        "description": "Number of open tasks past their scheduled due date",
    },
    "milestone_slippage": {
        "category": "schedule",
        "signal_type": "milestone_slippage",
        "warning_threshold": 3.0,
        "critical_threshold": 7.0,
        "unit": "days",
        "description": "Projected milestone completion date slipping beyond target date in days",
    },
    "aging_work": {
        "category": "schedule",
        "signal_type": "aging_work",
        "warning_threshold": 4.0,
        "critical_threshold": 8.0,
        "unit": "count",
        "description": "Number of in-progress tasks with no activity updates in > 14 days",
    },

    # 2. Dependency
    "blocked_tasks": {
        "category": "dependency",
        "signal_type": "blocked_tasks",
        "warning_threshold": 2.0,
        "critical_threshold": 4.0,
        "unit": "count",
        "description": "Number of open work items currently blocked by prerequisite tasks",
    },
    "overdue_upstream_dependencies": {
        "category": "dependency",
        "signal_type": "overdue_upstream_dependencies",
        "warning_threshold": 1.0,
        "critical_threshold": 3.0,
        "unit": "count",
        "description": "Prerequisite blocker tasks that are overdue while blocking downstream deliverables",
    },
    "dependency_concentration": {
        "category": "dependency",
        "signal_type": "dependency_concentration",
        "warning_threshold": 3.0,
        "critical_threshold": 5.0,
        "unit": "dependents",
        "description": "Single work item acting as a blocker for multiple downstream items",
    },

    # 3. Scope
    "unestimated_scope_growth": {
        "category": "scope",
        "signal_type": "unestimated_scope_growth",
        "warning_threshold": 2.0,
        "critical_threshold": 5.0,
        "unit": "count",
        "description": "Unestimated tasks or scope creep added midway to in-flight milestones",
    },
    "requirement_churn": {
        "category": "scope",
        "signal_type": "requirement_churn",
        "warning_threshold": 3.0,
        "critical_threshold": 6.0,
        "unit": "count",
        "description": "Work items exhibiting frequent priority shifts, label changes, or scope rework",
    },

    # 4. Capacity
    "workload_concentration": {
        "category": "capacity",
        "signal_type": "workload_concentration",
        "warning_threshold": 35.0,
        "critical_threshold": 50.0,
        "unit": "percent",
        "description": "Percentage of total active/critical tasks assigned to a single developer (Bus Factor)",
    },
    "excessive_wip": {
        "category": "capacity",
        "signal_type": "excessive_wip",
        "warning_threshold": 3.0,
        "critical_threshold": 5.0,
        "unit": "tasks_per_dev",
        "description": "Concurrent in-progress tasks assigned to a single engineer exceeding WIP limits",
    },
    "single_owner_bottleneck": {
        "category": "capacity",
        "signal_type": "single_owner_bottleneck",
        "warning_threshold": 3.0,
        "critical_threshold": 5.0,
        "unit": "critical_tasks",
        "description": "Critical-priority milestone deliverables assigned to a single person",
    },

    # 5. Quality
    "defect_growth": {
        "category": "quality",
        "signal_type": "defect_growth",
        "warning_threshold": 20.0,
        "critical_threshold": 35.0,
        "unit": "percent",
        "description": "Defects / bugs as a percentage of total open project deliverables",
    },
    "reopened_issues": {
        "category": "quality",
        "signal_type": "reopened_issues",
        "warning_threshold": 1.0,
        "critical_threshold": 3.0,
        "unit": "count",
        "description": "Defect tickets that have been reopened after initial resolution",
    },
    "critical_defect_debt": {
        "category": "quality",
        "signal_type": "critical_defect_debt",
        "warning_threshold": 1.0,
        "critical_threshold": 3.0,
        "unit": "count",
        "description": "Open critical or high-severity bugs open and unresolved",
    },

    # 6. Budget
    "budget_variance": {
        "category": "budget",
        "signal_type": "budget_variance",
        "warning_threshold": 5.0,
        "critical_threshold": 15.0,
        "unit": "percent",
        "description": "Actual financial expenditure exceeding planned baseline by percentage",
    },
    "burn_rate_acceleration": {
        "category": "budget",
        "signal_type": "burn_rate_acceleration",
        "warning_threshold": 1.10,
        "critical_threshold": 1.25,
        "unit": "ratio",
        "description": "Cost Performance Index drift / expenditure acceleration multiplier",
    },

    # 7. Decision Latency
    "long_running_blockers": {
        "category": "decision",
        "signal_type": "long_running_blockers",
        "warning_threshold": 4.0,
        "critical_threshold": 8.0,
        "unit": "days",
        "description": "Days an active work item has remained blocked without resolution",
    },
    "stalled_pr_reviews": {
        "category": "decision",
        "signal_type": "stalled_pr_reviews",
        "warning_threshold": 3.0,
        "critical_threshold": 6.0,
        "unit": "days",
        "description": "Pull requests awaiting code review or architectural sign-off in days",
    },
    "unresolved_decisions": {
        "category": "decision",
        "signal_type": "unresolved_decisions",
        "warning_threshold": 5.0,
        "critical_threshold": 10.0,
        "unit": "days",
        "description": "Architecture RFCs or decision-needed tickets pending resolution in days",
    },
}


def get_merged_thresholds(db_thresholds: list[Any]) -> dict[str, dict[str, float]]:
    """Merge system default thresholds with project-specific database overrides.

    Returns dict keyed by signal_type mapping to {'warning': float, 'critical': float}.
    """
    merged: dict[str, dict[str, float]] = {}
    for sig_type, def_data in DEFAULT_THRESHOLDS.items():
        merged[sig_type] = {
            "warning": float(def_data["warning_threshold"]),
            "critical": float(def_data["critical_threshold"]),
        }

    for db_t in db_thresholds:
        if db_t.signal_type in merged:
            merged[db_t.signal_type]["warning"] = float(db_t.warning_threshold)
            merged[db_t.signal_type]["critical"] = float(db_t.critical_threshold)

    return merged
