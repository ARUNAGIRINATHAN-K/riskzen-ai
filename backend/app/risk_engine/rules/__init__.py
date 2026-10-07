"""Risk Engine Rule Registry - All 7 Risk Categories."""
from typing import List, Type

from app.risk_engine.base_rule import BaseRiskRule
from app.risk_engine.rules.budget import BudgetVarianceRule, BurnRateAccelerationRule
from app.risk_engine.rules.capacity import (
    ExcessiveWIPRule,
    SingleOwnerBottleneckRule,
    WorkloadConcentrationRule,
)
from app.risk_engine.rules.decision import LongRunningBlockersRule, StalledPRReviewsRule
from app.risk_engine.rules.dependency import (
    BlockedTasksRule,
    DependencyConcentrationRule,
    OverdueUpstreamDependenciesRule,
)
from app.risk_engine.rules.quality import (
    CriticalDefectDebtRule,
    DefectGrowthRule,
    ReopenedIssuesRule,
)
from app.risk_engine.rules.schedule import (
    AgingWorkRule,
    MilestoneSlippageRule,
    OverdueTasksRule,
)
from app.risk_engine.rules.scope import RequirementChurnRule, ScopeGrowthRule

# Master registry of all active deterministic risk rules
ALL_RULES: List[Type[BaseRiskRule]] = [
    # 1. Schedule Risk
    OverdueTasksRule,
    MilestoneSlippageRule,
    AgingWorkRule,
    # 2. Dependency Risk
    BlockedTasksRule,
    OverdueUpstreamDependenciesRule,
    DependencyConcentrationRule,
    # 3. Scope Risk
    ScopeGrowthRule,
    RequirementChurnRule,
    # 4. Capacity Risk
    WorkloadConcentrationRule,
    ExcessiveWIPRule,
    SingleOwnerBottleneckRule,
    # 5. Quality Risk
    DefectGrowthRule,
    CriticalDefectDebtRule,
    ReopenedIssuesRule,
    # 6. Budget Risk
    BudgetVarianceRule,
    BurnRateAccelerationRule,
    # 7. Decision Risk
    LongRunningBlockersRule,
    StalledPRReviewsRule,
]


def get_all_rules() -> List[BaseRiskRule]:
    """Instantiate and return all registered risk rules."""
    return [rule_cls() for rule_cls in ALL_RULES]
