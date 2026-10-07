"""Unit tests for Risk Scoring Engine."""
import pytest

from app.models.risk import RiskCategory, RiskSeverity
from app.risk_engine.base_rule import RiskSignal
from app.risk_engine.scoring import (
    calculate_category_score,
    calculate_project_risk_score,
)


def test_category_score_empty_signals():
    """Empty signals should yield 0.0 score and LOW severity."""
    res = calculate_category_score(RiskCategory.SCHEDULE, [])
    assert res.score == 0.0
    assert res.severity == RiskSeverity.LOW
    assert res.signal_count == 0


def test_category_score_critical_signals():
    """Presence of a critical signal elevates the category score."""
    sig = RiskSignal(
        rule_id="TEST_001",
        category=RiskCategory.SCHEDULE,
        signal_type="TEST_CRITICAL",
        severity=RiskSeverity.CRITICAL,
        confidence=0.90,
        title="Test Critical",
        description="Desc",
        score=0.85,
    )
    res = calculate_category_score(RiskCategory.SCHEDULE, [sig])
    assert res.score >= 0.80
    assert res.severity == RiskSeverity.CRITICAL


def test_project_risk_score_aggregation():
    """Test overall project risk score weighted aggregation across multiple categories."""
    sig1 = RiskSignal(
        rule_id="SCH_001",
        category=RiskCategory.SCHEDULE,
        signal_type="OVERDUE",
        severity=RiskSeverity.HIGH,
        confidence=0.85,
        title="Schedule Delay",
        description="Desc",
        score=0.60,
    )
    sig2 = RiskSignal(
        rule_id="CAP_001",
        category=RiskCategory.CAPACITY,
        signal_type="CONCENTRATION",
        severity=RiskSeverity.HIGH,
        confidence=0.80,
        title="Capacity Bottleneck",
        description="Desc",
        score=0.65,
    )

    proj_res = calculate_project_risk_score([sig1, sig2], data_quality_score=90.0)
    assert proj_res.total_signals == 2
    assert proj_res.confidence > 0.0
    assert RiskCategory.SCHEDULE.value in proj_res.category_scores
    assert RiskCategory.CAPACITY.value in proj_res.category_scores
    assert proj_res.category_scores[RiskCategory.SCHEDULE.value].score > 0.0
    assert proj_res.category_scores[RiskCategory.BUDGET.value].score == 0.0
