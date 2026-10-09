"""Automated Tests for Performance, Resilience, and Security.

Verifies:
- Risk engine executes 500+ work items under 500ms SLA
- Risk engine executes 1,000+ work items under 500ms SLA
- LLM timeout and network failure are handled gracefully without crashing host app
- Connector error containment
- Security audit checks (encryption at rest, parameterization, no secret leakage)
"""
import pytest

from app.evaluation.evaluate_resilience import ResilienceEvaluator


def test_rule_engine_500_items_load_performance():
    """500+ work items risk evaluation must complete within 500ms SLA."""
    res = ResilienceEvaluator.benchmark_rule_engine(item_count=500)

    assert res.item_count == 500
    assert res.passed_sub_500ms_sla is True
    assert res.execution_time_ms < 500.0
    assert res.throughput_items_per_sec > 1000.0


def test_rule_engine_1000_items_load_performance():
    """1,000+ work items risk evaluation must complete within 500ms SLA."""
    res = ResilienceEvaluator.benchmark_rule_engine(item_count=1000)

    assert res.item_count == 1000
    assert res.passed_sub_500ms_sla is True
    assert res.execution_time_ms < 500.0
    assert res.throughput_items_per_sec > 2000.0


def test_llm_timeout_resilience_and_graceful_degradation():
    """System must degrade gracefully without crashing when LLM times out."""
    res = ResilienceEvaluator.evaluate_llm_resilience_and_fallback()

    assert res.graceful_degradation_passed is True
    assert "timeout" in res.failure_simulated.lower()


def test_connector_failure_resilience():
    """Connector network failure must be contained without corrupting project data."""
    res = ResilienceEvaluator.evaluate_connector_resilience()

    assert res.graceful_degradation_passed is True


def test_security_audit_checks():
    """All security baseline checks must pass."""
    checks = ResilienceEvaluator.run_security_audit_checks()

    assert len(checks) >= 5
    for c in checks:
        assert c.passed is True, f"Security check {c.check_id} failed: {c.title}"


def test_complete_system_evaluation_suite():
    """Full evaluation suite must verify all SLAs and security conditions."""
    suite = ResilienceEvaluator.run_complete_suite()

    assert suite.all_slas_met is True
    assert len(suite.load_benchmarks) >= 2
    assert len(suite.resilience_tests) >= 2
    assert len(suite.security_checks) >= 5
