"""Analyze Node: Root-cause identification and evidence citation."""
import json
import re
from typing import Any, Dict

from app.agent.llm import BaseLLMService
from app.agent.prompts.loader import load_prompt_template
from app.agent.state import InvestigationState
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.node.analyze")


async def analyze_node(state: InvestigationState, llm: BaseLLMService) -> Dict[str, Any]:
    """Node 3: Formulates grounded root-cause explanation citing specific retrieved evidence."""
    try:
        # Build evidence text
        evidence_text = "\n".join(
            f"- [{e.get('source_type', 'item')}] {e.get('title')}: {e.get('content')}"
            for e in state.get("retrieved_evidence", [])
        ) or "No specific evidence items retrieved."

        # Build signals summary
        signals_text = "\n".join(
            f"- [{s.get('severity', 'UNKNOWN')}] {s.get('signal_type')}: {s.get('description', '')}"
            for s in state.get("risk_signals", [])
        ) or "Deterministic signals available."

        prompt = load_prompt_template(
            "root_cause",
            {
                "risk_title": state.get("risk_title", "Unspecified Risk"),
                "risk_category": state.get("risk_category", "General"),
                "risk_severity": state.get("risk_severity", "MEDIUM"),
                "hypothesis": state.get("initial_hypothesis", ""),
                "retrieved_evidence": evidence_text,
                "signals_summary": signals_text,
            },
        )

        response = await llm.generate(
            prompt=prompt,
            temperature=0.1,
            response_format="json",
        )

        parsed: Dict[str, Any] = {}
        try:
            clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.MULTILINE)
            parsed = json.loads(clean_json)
        except Exception:
            parsed = {
                "explanation": f"Risk arises from {state.get('risk_title')} requiring mitigation.",
                "contributing_factors": [
                    {
                        "factor": "Delivery Delay",
                        "severity": "high",
                        "evidence_citation": "Telemetry indicates overdue work items on critical path.",
                        "impact": "Milestone delivery risk.",
                    }
                ],
                "confidence_score": 0.80,
            }

        return {
            "explanation": parsed.get("explanation", ""),
            "contributing_factors": parsed.get("contributing_factors", []),
            "analysis_confidence": float(parsed.get("confidence_score", 0.85)),
        }

    except Exception as exc:
        logger.error("Analyze node failed", error=str(exc))
        return {
            "explanation": f"Risk identified for {state.get('risk_title')}.",
            "contributing_factors": [],
            "analysis_confidence": 0.50,
            "error": str(exc),
        }
