"""Evaluation Package for RiskZen.

Includes:
- Historical scenarios generator (Scenario A, B, C)
- Deterministic detection precision/recall/lead-time evaluator
- AI investigation quality and grounding evaluator
- Performance load benchmarking and resilience evaluator
"""
from app.evaluation.evaluate_detection import (
    DetectionEvaluationReport,
    DetectionEvaluator,
    ScenarioEvaluationResult,
)
from app.evaluation.evaluate_investigation import (
    AgentEvaluationReport,
    InvestigationEvaluator,
    InvestigationQualityScore,
)
from app.evaluation.evaluate_resilience import (
    LoadBenchmarkResult,
    ResilienceEvaluator,
    ResilienceTestResult,
    SecurityAuditResult,
    SystemEvaluationSuiteResult,
)
from app.evaluation.historical_scenarios import (
    GroundTruthRisk,
    HistoricalScenario,
    create_scenario_a_blocked_dependency,
    create_scenario_b_scope_creep,
    create_scenario_c_healthy_sprint,
    get_all_historical_scenarios,
)

__all__ = [
    "GroundTruthRisk",
    "HistoricalScenario",
    "create_scenario_a_blocked_dependency",
    "create_scenario_b_scope_creep",
    "create_scenario_c_healthy_sprint",
    "get_all_historical_scenarios",
    "DetectionEvaluator",
    "DetectionEvaluationReport",
    "ScenarioEvaluationResult",
    "InvestigationEvaluator",
    "AgentEvaluationReport",
    "InvestigationQualityScore",
    "ResilienceEvaluator",
    "LoadBenchmarkResult",
    "ResilienceTestResult",
    "SecurityAuditResult",
    "SystemEvaluationSuiteResult",
]
