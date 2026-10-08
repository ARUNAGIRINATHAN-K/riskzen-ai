"""Investigate Node: Assembles context and reasons over structured risk signals."""
import json
import re
from typing import Any, Dict

from app.agent.llm import BaseLLMService, get_llm_service
from app.agent.prompts.loader import load_prompt_template
from app.agent.state import InvestigationState
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.node.investigate")


async def investigate_node(state: InvestigationState, llm: BaseLLMService) -> Dict[str, Any]:
    """Node 1: Reasons over risk signals and formulates preliminary hypotheses & evidence queries."""
    try:
        # Build signals summary text
        signals_text = "\n".join(
            f"- [{s.get('severity', 'UNKNOWN')}] {s.get('signal_type')}: {s.get('description', '')}"
            for s in state.get("risk_signals", [])
        ) or "No detailed signals attached."

        # Build project context text
        ctx = state.get("project_context", {})
        proj_text = (
            f"Project: {ctx.get('project_name', 'Unknown')}\n"
            f"Total Work Items: {ctx.get('total_work_items', 0)} | Overdue Items: {ctx.get('overdue_items_count', 0)}\n"
            f"Active Team Members: {ctx.get('active_members_count', 0)}\n"
            f"Milestones: {', '.join(ctx.get('milestones_summary', []))}"
        )

        prompt = load_prompt_template(
            "investigation",
            {
                "risk_title": state.get("risk_title", "Unspecified Risk"),
                "risk_category": state.get("risk_category", "General"),
                "risk_severity": state.get("risk_severity", "MEDIUM"),
                "signals_summary": signals_text,
                "project_context": proj_text,
            },
        )

        response = await llm.generate(
            prompt=prompt,
            temperature=0.1,
            response_format="json",
        )

        # Parse JSON
        parsed: Dict[str, Any] = {}
        try:
            # Handle potential markdown code fencing in LLM response
            clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.MULTILINE)
            parsed = json.loads(clean_json)
        except Exception:
            parsed = {
                "initial_hypothesis": f"Risk detected in {state.get('risk_category')}: {state.get('risk_title')}",
                "scope_of_investigation": "Evaluate associated work items and dependencies.",
                "key_questions": ["What is causing the delay?", "Who is impacted?"],
                "recommended_evidence_queries": [state.get("risk_title", "risk"), "overdue tasks", "blockers"],
            }

        return {
            "initial_hypothesis": parsed.get("initial_hypothesis", ""),
            "scope_of_investigation": parsed.get("scope_of_investigation", ""),
            "key_questions": parsed.get("key_questions", []),
            "evidence_queries": parsed.get("recommended_evidence_queries", [state.get("risk_title", "")]),
        }

    except Exception as exc:
        logger.error("Investigate node failed", error=str(exc))
        return {
            "initial_hypothesis": f"Risk investigation for {state.get('risk_title')}",
            "scope_of_investigation": "General project telemetry analysis.",
            "key_questions": [],
            "evidence_queries": [state.get("risk_title", "")],
            "error": str(exc),
        }
