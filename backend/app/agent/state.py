"""State Definition for LangGraph Risk Investigation Workflow."""
from typing import Any, Dict, List, Optional, TypedDict


class ContributingFactor(TypedDict):
    factor: str
    severity: str  # high, medium, low
    evidence_citation: str
    impact: str


class RecommendationItem(TypedDict):
    action_description: str
    rationale: str
    suggested_owner: str
    urgency: str  # immediate, today, this_week, optional


class InvestigationState(TypedDict):
    """The shared state object traversing all nodes in the LangGraph workflow."""

    risk_event_id: str
    project_id: str
    risk_title: str
    risk_category: str
    risk_severity: str
    affected_milestone_id: Optional[str]

    # Structured Signals from Risk Detection Engine
    risk_signals: List[Dict[str, Any]]
    project_context: Dict[str, Any]

    # Node 1: Investigation Output
    initial_hypothesis: str
    scope_of_investigation: str
    key_questions: List[str]
    evidence_queries: List[str]

    # Node 2: Evidence Retrieval Output
    retrieved_evidence: List[Dict[str, Any]]

    # Node 3: Root Cause Analysis Output
    explanation: str
    contributing_factors: List[ContributingFactor]
    analysis_confidence: float

    # Node 4: Recommendations Output
    recommendations: List[RecommendationItem]

    # Node 5: Review / Quality Guard Output
    quality_check_passed: bool
    review_feedback: str
    hallucination_detected: bool

    # Workflow Control
    retry_count: int
    error: Optional[str]
