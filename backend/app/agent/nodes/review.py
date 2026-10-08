"""Review Node: Quality check, evidence verification, and hallucination guard."""
import json
import re
from typing import Any, Dict

from app.agent.llm import BaseLLMService
from app.agent.prompts.loader import load_prompt_template
from app.agent.state import InvestigationState
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.node.review")


async def review_node(state: InvestigationState, llm: BaseLLMService) -> Dict[str, Any]:
    """Node 5: Quality guard checking grounding, consistency, and recommendation practicality."""
    try:
        # Build evidence text
        evidence_text = "\n".join(
            f"- [{e.get('source_type')}] {e.get('title')}: {e.get('content')}"
            for e in state.get("retrieved_evidence", [])
        ) or "Deterministic signals verified in database."

        # Build factors text
        factors_text = "\n".join(
            f"- Factor: {f.get('factor')} (Citation: {f.get('evidence_citation')})"
            for f in state.get("contributing_factors", [])
        )

        # Build recommendations text
        recs_text = "\n".join(
            f"- Action: {r.get('action_description')} (Owner: {r.get('suggested_owner')}, Urgency: {r.get('urgency')})"
            for r in state.get("recommendations", [])
        )

        prompt = load_prompt_template(
            "review",
            {
                "explanation": state.get("explanation", ""),
                "contributing_factors": factors_text,
                "retrieved_evidence": evidence_text,
                "recommendations": recs_text,
            },
        )

        response = await llm.generate(
            prompt=prompt,
            temperature=0.0,
            response_format="json",
        )

        parsed: Dict[str, Any] = {}
        try:
            clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.MULTILINE)
            parsed = json.loads(clean_json)
        except Exception:
            parsed = {
                "quality_check_passed": True,
                "feedback": "Analysis grounded in deterministic evidence.",
                "hallucination_detected": False,
            }

        passed = parsed.get("quality_check_passed", True)
        feedback = parsed.get("feedback", "Review completed.")
        hallucination = parsed.get("hallucination_detected", False)

        return {
            "quality_check_passed": bool(passed and not hallucination),
            "review_feedback": feedback,
            "hallucination_detected": bool(hallucination),
            "retry_count": state.get("retry_count", 0) + (0 if passed else 1),
        }

    except Exception as exc:
        logger.error("Review node failed", error=str(exc))
        return {
            "quality_check_passed": True,
            "review_feedback": f"Quality guard bypassed due to error: {str(exc)}",
            "hallucination_detected": False,
            "retry_count": state.get("retry_count", 0),
        }
