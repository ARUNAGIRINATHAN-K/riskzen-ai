"""Automated Tests for Phase 5 Evaluation Pipeline.

Verifies:
- Scenario A (Blocked Dependency) detects Critical schedule & dependency risks
- Scenario B (Scope Creep) detects High scope & capacity risks
- Scenario C (Healthy Sprint) produces 0 Critical alerts and passes as Healthy
- Precision >= 60% and Recall >= 70%
- Lead-time detection calculation
- AI investigation quality and grounding verification
- Evaluation API endpoints
"""
import pytest
from httpx import AsyncClient

from app.evaluation import (
    DetectionEvaluator,
    InvestigationEvaluator,
    create_scenario_a_blocked_dependency,
    create_scenario_b_scope_creep,
    create_scenario_c_healthy_sprint,
    get_all_historical_scenarios,
)


def test_scenario_a_blocked_dependency_detection():
    """Scenario A should detect blocked tasks and overdue tasks with high/critical severity."""
    scenario = create_scenario_a_blocked_dependency()
    evaluator = DetectionEvaluator()
    res = evaluator.evaluate_scenario(scenario)

    assert res.scenario_id == "scenario_a_blocked_dependency"
    assert res.signals_detected >= 2
    assert res.critical_signals + res.high_signals >= 2
    assert res.true_positives >= 2
    assert res.false_negatives == 0
    assert res.precision >= 0.60
    assert res.recall >= 0.80
    assert res.average_lead_time_days > 0.0
    assert res.overall_health in ["critical", "at_risk"]


def test_scenario_b_scope_creep_detection():
    """Scenario B should detect scope growth and capacity bottleneck."""
    scenario = create_scenario_b_scope_creep()
    evaluator = DetectionEvaluator()
    res = evaluator.evaluate_scenario(scenario)

    assert res.scenario_id == "scenario_b_scope_creep"
    assert res.signals_detected >= 2
    assert res.true_positives >= 1
    assert res.precision >= 0.50
    assert res.recall >= 0.50
    assert res.overall_health in ["critical", "at_risk"]


def test_scenario_c_healthy_sprint_detection():
    """Scenario C should NOT produce any Critical or High alerts."""
    scenario = create_scenario_c_healthy_sprint()
    evaluator = DetectionEvaluator()
    res = evaluator.evaluate_scenario(scenario)

    assert res.scenario_id == "scenario_c_healthy_sprint"
    assert res.critical_signals == 0
    assert res.high_signals == 0
    assert res.overall_health == "healthy"
    assert res.composite_risk_score < 35.0


def test_full_detection_evaluation_report():
    """Aggregate evaluation report must meet pre-pilot baseline requirements."""
    evaluator = DetectionEvaluator()
    report = evaluator.run_full_evaluation()

    assert report.total_scenarios == 3
    assert report.total_true_positives >= 3
    assert report.meets_precision_target is True
    assert report.overall_precision >= 0.60
    assert report.overall_recall >= 0.70
    assert report.average_lead_time_days >= 3.0


def test_ai_investigation_quality_evaluation():
    """LangGraph agent investigation quality must score >= 3.0 on 1-5 rubric."""
    evaluator = InvestigationEvaluator()
    report = evaluator.run_agent_evaluation()

    assert report.total_investigations >= 2
    assert report.average_grounding >= 3.5
    assert report.average_logical_attribution >= 3.5
    assert report.average_actionability >= 3.5
    assert report.overall_quality_score >= 3.0
    assert report.hallucination_free_rate >= 0.95
    assert report.meets_quality_target is True


@pytest.mark.asyncio
async def test_evaluation_api_endpoints(client: AsyncClient):
    """Evaluation REST APIs should return structured reports."""
    # 1. Detection report
    det_res = await client.get("/api/v1/evaluation/detection")
    assert det_res.status_code == 200
    det_data = det_res.json()
    assert det_data["total_scenarios"] == 3
    assert "overall_precision" in det_data

    # 2. Investigation report
    inv_res = await client.get("/api/v1/evaluation/investigation")
    assert inv_res.status_code == 200
    inv_data = inv_res.json()
    assert inv_data["meets_quality_target"] is True

    # 3. Resilience report
    res_res = await client.get("/api/v1/evaluation/resilience")
    assert res_res.status_code == 200
    res_data = res_res.json()
    assert res_data["all_slas_met"] is True

    # 4. Full evaluation report
    full_res = await client.get("/api/v1/evaluation/report")
    assert full_res.status_code == 200
    full_data = full_res.json()
    assert full_data["status"] == "success"
    assert full_data["exit_criteria_summary"]["historical_scenarios_tested"] is True
    assert full_data["exit_criteria_summary"]["precision_ge_60_pct"] is True
