"""Retrieve Evidence Node: Executes semantic and structural searches."""
import uuid
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.embeddings import EvidenceRetrievalService
from app.agent.state import InvestigationState
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.node.retrieve_evidence")


async def retrieve_evidence_node(
    state: InvestigationState, session: AsyncSession
) -> Dict[str, Any]:
    """Node 2: Fetches verified evidence records from project database and embeddings."""
    try:
        project_id = uuid.UUID(state["project_id"])
        queries = state.get("evidence_queries", [state.get("risk_title", "")])
        
        milestone_id = None
        if state.get("affected_milestone_id"):
            try:
                milestone_id = uuid.UUID(state["affected_milestone_id"])
            except Exception:
                pass

        evidence_list = await EvidenceRetrievalService.retrieve_evidence(
            session=session,
            project_id=project_id,
            queries=queries,
            affected_milestone_id=milestone_id,
            top_k=6,
        )

        return {
            "retrieved_evidence": evidence_list,
        }

    except Exception as exc:
        logger.error("Retrieve evidence node failed", error=str(exc))
        return {
            "retrieved_evidence": [],
            "error": str(exc),
        }
