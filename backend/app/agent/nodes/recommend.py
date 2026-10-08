"""Recommend Node: Generates 2–4 practical, actionable mitigation recommendations."""
import json
import re
from typing import Any, Dict

from app.agent.llm import BaseLLMService
from app.agent.prompts.loader import load_prompt_template
from app.agent.state import InvestigationState
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.node.recommend")


async def recommend_node(state: InvestigationState, llm: BaseLLMService) -> Dict[str, Any]:
    """Node 4: Produces practical, actionable recommendations with assigned owners and urgency."""
    try:
        # Format contributing factors
        factors_text = "\n".join(
            f"- Factor: {f.get('factor')} [Severity: {f.get('severity')}]\n"
            f"  Citation: {f.get('evidence_citation')}\n"
            f"  Impact: {f.get('impact')}"
            for f in state.get("contributing_factors", [])
        ) or "Key project telemetry signals."

        # Format team members from project context
        ctx = state.get("project_context", {})
        members = ctx.get("team_members", [])
        members_text = "\n".join(
            f"- {m.get('name', 'Member')} ({m.get('role', 'Developer')})"
            for m in members
        ) if members else "- Project Lead\n- Tech Lead\n- Scrum Master\n- Project Manager"

        prompt = load_prompt_template(
            "recommendation",
            {
                "risk_title": state.get("risk_title", "Unspecified Risk"),
                "risk_category": state.get("risk_category", "General"),
                "explanation": state.get("explanation", ""),
                "contributing_factors": factors_text,
                "team_members": members_text,
            },
        )

        response = await llm.generate(
            prompt=prompt,
            temperature=0.2,
            response_format="json",
        )

        parsed: Dict[str, Any] = {}
        try:
            clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.MULTILINE)
            parsed = json.loads(clean_json)
        except Exception:
            parsed = {
                "recommendations": [
                    {
                        "action_description": f"Review and unblock deliverables related to {state.get('risk_title')}.",
                        "rationale": "Directly resolves active delivery bottleneck.",
                        "suggested_owner": "Project Lead",
                        "urgency": "immediate",
                    }
                ]
            }

        recs = parsed.get("recommendations", [])
        # Ensure urgency values are valid
        valid_urgencies = {"immediate", "today", "this_week", "optional"}
        for r in recs:
            if r.get("urgency") not in valid_urgencies:
                r["urgency"] = "this_week"

        return {
            "recommendations": recs,
        }

    except Exception as exc:
        logger.error("Recommend node failed", error=str(exc))
        return {
            "recommendations": [],
            "error": str(exc),
        }
