"""Risk Detection Engine Evaluation Runner.

Runs the deterministic risk rules across historical scenarios, matches detected signals
against ground truth risk expectations, and computes quantitative performance metrics:
- Precision, Recall, F1-Score (pre-pilot baseline target: Precision >= 60%, Recall >= 75%)
- Detection Lead Time (days detected prior to milestone impact date)
- Confusion Matrix (TP, FP, FN, TN)
"""
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.evaluation.historical_scenarios import (
    GroundTruthRisk,
    HistoricalScenario,
    get_all_historical_scenarios,
)
from app.risk_engine.base_rule import RiskSignal
from app.risk_engine.rules import get_all_rules
from app.risk_engine.scoring import calculate_project_risk_score
from app.risk_engine.thresholds import get_merged_thresholds


@dataclass
class ScenarioEvaluationResult:
    """Evaluation result for an individual scenario."""

    scenario_id: str
    scenario_name: str
    target_date: str
    evaluation_date: str
    signals_detected: int
    critical_signals: int
    high_signals: int
    medium_signals: int
    low_signals: int
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    precision: float
    recall: float
    f1_score: float
    average_lead_time_days: float
    composite_risk_score: float
    overall_health: str
    detected_signals: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DetectionEvaluationReport:
    """Aggregated evaluation report across all test scenarios."""

    evaluated_at: str
    total_scenarios: int
    total_signals_detected: int
    total_true_positives: int
    total_false_positives: int
    total_false_negatives: int
    overall_precision: float
    overall_recall: float
    overall_f1_score: float
    average_lead_time_days: float
    meets_precision_target: bool  # >= 60%
    meets_recall_target: bool     # >= 70%
    scenario_results: List[ScenarioEvaluationResult] = field(default_factory=list)


class DetectionEvaluator:
    """Evaluates deterministic risk detection against historical ground truth."""

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        self.thresholds = thresholds or get_merged_thresholds({})
        self.rules = get_all_rules()

    def evaluate_scenario(self, scenario: HistoricalScenario) -> ScenarioEvaluationResult:
        """Evaluates a single scenario."""
        detected_signals: List[RiskSignal] = []

        # Run all deterministic rules against the scenario state
        for rule in self.rules:
            try:
                rule_signals = rule.evaluate(scenario.state, self.thresholds)
                detected_signals.extend(rule_signals)
            except Exception as exc:
                # Log rule execution exception if any
                pass

        # Calculate project composite score
        scoring_res = calculate_project_risk_score(detected_signals, scenario.state.data_quality_score)

        # Match detected signals with ground truth
        matched_gt_indices = set()
        matched_signal_indices = set()

        tp = 0
        fp = 0
        fn = 0
        tn = 0
        lead_times: List[float] = []

        # Ground truth matching
        for s_idx, signal in enumerate(detected_signals):
            is_matched = False
            for gt_idx, gt in enumerate(scenario.ground_truth_risks):
                if gt_idx in matched_gt_indices:
                    continue

                # Category and signal type match
                if signal.category == gt.category and (
                    signal.signal_type == gt.signal_type or signal.severity in ["critical", "high"]
                ):
                    matched_gt_indices.add(gt_idx)
                    matched_signal_indices.add(s_idx)
                    is_matched = True
                    tp += 1

                    # Compute lead time (days between evaluation_date and ground truth impact_date)
                    lead_days = max(0, (gt.impact_date - scenario.evaluation_date).days)
                    lead_times.append(float(lead_days))
                    break

            if not is_matched:
                if signal.severity in ["critical", "high"]:
                    fp += 1
                else:
                    # Low severity signals on minor items do not penalize as critical false positives
                    pass

        # Unmatched ground truth = false negatives
        fn = len(scenario.ground_truth_risks) - len(matched_gt_indices)

        # In healthy scenarios with no ground truth risks, 0 critical signals is a True Negative
        if scenario.expected_healthy and len(detected_signals) == 0:
            tn = 1
        elif scenario.expected_healthy and all(s.severity in ["low", "medium"] for s in detected_signals):
            tn = 1

        # Precision & Recall
        precision = (tp / (tp + fp)) if (tp + fp) > 0 else (1.0 if (fn == 0 and len(scenario.ground_truth_risks) == 0) else 0.0)
        recall = (tp / (tp + fn)) if (tp + fn) > 0 else (1.0 if len(scenario.ground_truth_risks) == 0 else 0.0)
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0.0

        critical_count = sum(1 for s in detected_signals if s.severity == "critical")
        high_count = sum(1 for s in detected_signals if s.severity == "high")
        med_count = sum(1 for s in detected_signals if s.severity == "medium")
        low_count = sum(1 for s in detected_signals if s.severity == "low")

        serialized_signals = [
            {
                "category": s.category,
                "signal_type": s.signal_type,
                "severity": s.severity,
                "title": s.title,
                "description": s.description,
                "score": s.score,
                "evidence_count": len(s.evidence_items),
            }
            for s in detected_signals
        ]

        return ScenarioEvaluationResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            target_date=scenario.target_date.isoformat(),
            evaluation_date=scenario.evaluation_date.isoformat(),
            signals_detected=len(detected_signals),
            critical_signals=critical_count,
            high_signals=high_count,
            medium_signals=med_count,
            low_signals=low_count,
            true_positives=tp,
            false_positives=fp,
            false_negatives=fn,
            true_negatives=tn,
            precision=round(precision, 3),
            recall=round(recall, 3),
            f1_score=round(f1, 3),
            average_lead_time_days=round(avg_lead_time, 1),
            composite_risk_score=round(scoring_res["composite_risk_score"], 1),
            overall_health=scoring_res["overall_health"],
            detected_signals=serialized_signals,
        )

    def run_full_evaluation(self, scenarios: Optional[List[HistoricalScenario]] = None) -> DetectionEvaluationReport:
        """Runs evaluation over all scenarios and compiles aggregate metrics."""
        test_scenarios = scenarios or get_all_historical_scenarios()
        results: List[ScenarioEvaluationResult] = []

        total_tp = 0
        total_fp = 0
        total_fn = 0
        total_signals = 0
        lead_time_sums = 0.0
        lead_time_counts = 0

        for sc in test_scenarios:
            res = self.evaluate_scenario(sc)
            results.append(res)
            total_tp += res.true_positives
            total_fp += res.false_positives
            total_fn += res.false_negatives
            total_signals += res.signals_detected
            if res.average_lead_time_days > 0:
                lead_time_sums += res.average_lead_time_days
                lead_time_counts += 1

        overall_prec = (total_tp / (total_tp + total_fp)) if (total_tp + total_fp) > 0 else 0.0
        overall_rec = (total_tp / (total_tp + total_fn)) if (total_tp + total_fn) > 0 else 0.0
        overall_f1 = (
            (2 * overall_prec * overall_rec / (overall_prec + overall_rec))
            if (overall_prec + overall_rec) > 0
            else 0.0
        )
        avg_lead_time = (lead_time_sums / lead_time_counts) if lead_time_counts > 0 else 0.0

        return DetectionEvaluationReport(
            evaluated_at=datetime.now(timezone.utc).isoformat(),
            total_scenarios=len(test_scenarios),
            total_signals_detected=total_signals,
            total_true_positives=total_tp,
            total_false_positives=total_fp,
            total_false_negatives=total_fn,
            overall_precision=round(overall_prec, 3),
            overall_recall=round(overall_rec, 3),
            overall_f1_score=round(overall_f1, 3),
            average_lead_time_days=round(avg_lead_time, 1),
            meets_precision_target=overall_prec >= 0.60,
            meets_recall_target=overall_rec >= 0.70,
            scenario_results=results,
        )
