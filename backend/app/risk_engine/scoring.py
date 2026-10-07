"""Risk Scoring Engine.

Calculates category-level propensity scores, overall project risk score,
determines risk severity levels, and computes confidence ratings.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.models.risk import RiskCategory, RiskSeverity
from app.risk_engine.base_rule import RiskSignal

# Default category weights for overall project score aggregation
DEFAULT_CATEGORY_WEIGHTS: Dict[RiskCategory, float] = {
    RiskCategory.SCHEDULE: 0.20,
    RiskCategory.DEPENDENCY: 0.15,
    RiskCategory.SCOPE: 0.15,
    RiskCategory.CAPACITY: 0.15,
    RiskCategory.QUALITY: 0.15,
    RiskCategory.BUDGET: 0.10,
    RiskCategory.DECISION: 0.10,
}

SEVERITY_WEIGHTS: Dict[RiskSeverity, float] = {
    RiskSeverity.LOW: 0.25,
    RiskSeverity.MEDIUM: 0.50,
    RiskSeverity.HIGH: 0.75,
    RiskSeverity.CRITICAL: 1.00,
}


@dataclass
class CategoryScoreResult:
    category: RiskCategory
    score: float  # 0.0 to 1.0
    severity: RiskSeverity
    signal_count: int
    signals: List[RiskSignal] = field(default_factory=list)


@dataclass
class ProjectRiskScoreResult:
    overall_score: float  # 0.0 to 1.0
    overall_severity: RiskSeverity
    confidence: float  # 0.0 to 1.0
    category_scores: Dict[str, CategoryScoreResult]
    total_signals: int
    critical_signals_count: int
    high_signals_count: int


def calculate_category_score(
    category: RiskCategory, signals: List[RiskSignal]
) -> CategoryScoreResult:
    """Calculates risk score for a single category based on its detected signals."""
    if not signals:
        return CategoryScoreResult(
            category=category,
            score=0.0,
            severity=RiskSeverity.LOW,
            signal_count=0,
            signals=[],
        )

    # Score calculation: combination of max signal score and density of signals
    max_signal_score = max(s.score for s in signals)
    avg_signal_score = sum(s.score for s in signals) / len(signals)
    
    # Severity multiplier for high/critical presence
    has_critical = any(s.severity == RiskSeverity.CRITICAL for s in signals)
    has_high = any(s.severity == RiskSeverity.HIGH for s in signals)

    # Blend: 60% max severity/score + 40% average severity/score
    raw_score = (0.60 * max_signal_score) + (0.40 * avg_signal_score)

    if has_critical:
        raw_score = max(raw_score, 0.80)
    elif has_high:
        raw_score = max(raw_score, 0.55)

    category_score = min(1.0, max(0.0, raw_score))

    # Determine category severity
    if category_score >= 0.70:
        severity = RiskSeverity.CRITICAL
    elif category_score >= 0.45:
        severity = RiskSeverity.HIGH
    elif category_score >= 0.20:
        severity = RiskSeverity.MEDIUM
    else:
        severity = RiskSeverity.LOW

    return CategoryScoreResult(
        category=category,
        score=round(category_score, 3),
        severity=severity,
        signal_count=len(signals),
        signals=signals,
    )


def calculate_project_risk_score(
    signals: List[RiskSignal],
    data_quality_score: Optional[float] = None,
    custom_category_weights: Optional[Dict[str, float]] = None,
) -> ProjectRiskScoreResult:
    """Calculates overall project risk score, category scores, and confidence."""
    # 1. Group signals by category
    signals_by_cat: Dict[RiskCategory, List[RiskSignal]] = {
        cat: [] for cat in RiskCategory
    }
    for sig in signals:
        signals_by_cat[sig.category].append(sig)

    # 2. Score each category
    category_results: Dict[str, CategoryScoreResult] = {}
    total_score = 0.0
    total_weight = 0.0

    weights = DEFAULT_CATEGORY_WEIGHTS.copy()
    if custom_category_weights:
        for k, v in custom_category_weights.items():
            try:
                cat_enum = RiskCategory(k)
                weights[cat_enum] = float(v)
            except (ValueError, TypeError):
                pass

    for cat in RiskCategory:
        cat_result = calculate_category_score(cat, signals_by_cat[cat])
        category_results[cat.value] = cat_result
        weight = weights.get(cat, 0.15)
        total_score += cat_result.score * weight
        total_weight += weight

    overall_score = total_score / total_weight if total_weight > 0 else 0.0

    # Boost overall score if there are critical signals
    critical_count = sum(1 for s in signals if s.severity == RiskSeverity.CRITICAL)
    high_count = sum(1 for s in signals if s.severity == RiskSeverity.HIGH)

    if critical_count >= 2:
        overall_score = max(overall_score, 0.75)
    elif critical_count == 1 or high_count >= 3:
        overall_score = max(overall_score, 0.50)

    overall_score = min(1.0, max(0.0, overall_score))

    # 3. Determine overall project severity
    if overall_score >= 0.70:
        overall_severity = RiskSeverity.CRITICAL
    elif overall_score >= 0.45:
        overall_severity = RiskSeverity.HIGH
    elif overall_score >= 0.20:
        overall_severity = RiskSeverity.MEDIUM
    else:
        overall_severity = RiskSeverity.LOW

    # 4. Confidence calculation
    dq_factor = (data_quality_score / 100.0) if data_quality_score is not None else 0.85
    # Signal depth factor
    signal_depth_factor = min(1.0, 0.6 + (len(signals) * 0.05))
    confidence = round(min(1.0, dq_factor * signal_depth_factor), 2)

    return ProjectRiskScoreResult(
        overall_score=round(overall_score, 3),
        overall_severity=overall_severity,
        confidence=confidence,
        category_scores=category_results,
        total_signals=len(signals),
        critical_signals_count=critical_count,
        high_signals_count=high_count,
    )
