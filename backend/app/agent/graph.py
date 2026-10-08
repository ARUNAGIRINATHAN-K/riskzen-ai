"""LangGraph Investigation Workflow Graph Definition."""
from typing import Any, Dict, Literal
from langgraph.graph import END, START, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm import BaseLLMService, get_llm_service
from app.agent.nodes.analyze import analyze_node
from app.agent.nodes.investigate import investigate_node
from app.agent.nodes.recommend import recommend_node
from app.agent.nodes.retrieve_evidence import retrieve_evidence_node
from app.agent.nodes.review import review_node
from app.agent.state import InvestigationState
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.graph")


def build_investigation_graph(session: AsyncSession, llm_service: BaseLLMService):
    """Constructs and compiles the LangGraph state machine for risk investigation."""
    builder = StateGraph(InvestigationState)

    # 1. Register Node Functions (binding session & llm)
    async def run_investigate(state: InvestigationState) -> Dict[str, Any]:
        return await investigate_node(state, llm_service)

    async def run_retrieve_evidence(state: InvestigationState) -> Dict[str, Any]:
        return await retrieve_evidence_node(state, session)

    async def run_analyze(state: InvestigationState) -> Dict[str, Any]:
        return await analyze_node(state, llm_service)

    async def run_recommend(state: InvestigationState) -> Dict[str, Any]:
        return await recommend_node(state, llm_service)

    async def run_review(state: InvestigationState) -> Dict[str, Any]:
        return await review_node(state, llm_service)

    builder.add_node("investigate", run_investigate)
    builder.add_node("retrieve_evidence", run_retrieve_evidence)
    builder.add_node("analyze", run_analyze)
    builder.add_node("recommend", run_recommend)
    builder.add_node("review", run_review)

    # 2. Add Linear Flow Edges
    builder.add_edge(START, "investigate")
    builder.add_edge("investigate", "retrieve_evidence")
    builder.add_edge("retrieve_evidence", "analyze")
    builder.add_edge("analyze", "recommend")
    builder.add_edge("recommend", "review")

    # 3. Add Conditional Edge for Quality Guard & Hallucination Retries
    def decide_post_review(state: InvestigationState) -> Literal["analyze", "__end__"]:
        if state.get("quality_check_passed", True):
            return END
        if state.get("retry_count", 0) >= 1:
            logger.warn("Max retries reached in quality review, concluding investigation with caveats")
            return END
        logger.info("Quality check failed, triggering 1-shot re-analysis retry")
        return "analyze"

    builder.add_conditional_edges(
        "review",
        decide_post_review,
        {
            "analyze": "analyze",
            END: END,
        },
    )

    return builder.compile()
