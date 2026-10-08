"""API Endpoints for AI Agent Investigation and Recommendation Lifecycle."""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.action import ActionResponse
from app.schemas.recommendation import (
    InvestigationTriggerResponse,
    RecommendationApproveRequest,
    RecommendationDismissRequest,
    RecommendationModifyRequest,
    RecommendationResponse,
    RecommendationSnoozeRequest,
)
from app.services.agent_service import AgentService
from app.services.auth_service import get_current_user

router = APIRouter(tags=["recommendations"])


@router.post(
    "/risks/{risk_id}/investigate",
    response_model=InvestigationTriggerResponse,
    summary="Trigger LangGraph AI agent investigation for a risk",
)
async def investigate_risk_event(
    risk_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvestigationTriggerResponse:
    """Executes the 5-node LangGraph investigation workflow and generates mitigation recommendations."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.investigate_risk(
            session=session,
            risk_event_id=risk_id,
            actor=user_identifier,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent investigation failed: {str(e)}",
        )


@router.get(
    "/risks/{risk_id}/recommendations",
    response_model=List[RecommendationResponse],
    summary="List mitigation recommendations for a risk event",
)
async def list_risk_recommendations(
    risk_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[RecommendationResponse]:
    """Retrieves all mitigation recommendations generated for a specific risk event."""
    return await AgentService.list_risk_recommendations(session=session, risk_event_id=risk_id)


@router.post(
    "/recommendations/{recommendation_id}/approve",
    response_model=ActionResponse,
    summary="Approve recommendation and create action item",
)
async def approve_recommendation(
    recommendation_id: uuid.UUID,
    body: RecommendationApproveRequest = RecommendationApproveRequest(),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionResponse:
    """Approves a recommendation, converts it into an actionable tracking item, and logs audit record."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.approve_recommendation(
            session=session,
            recommendation_id=recommendation_id,
            approve_req=body,
            actor=user_identifier,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/recommendations/{recommendation_id}/modify",
    response_model=ActionResponse,
    summary="Modify and approve recommendation",
)
async def modify_recommendation(
    recommendation_id: uuid.UUID,
    body: RecommendationModifyRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionResponse:
    """Modifies recommendation parameters and creates a tracked action item."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.modify_recommendation(
            session=session,
            recommendation_id=recommendation_id,
            modify_req=body,
            actor=user_identifier,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/recommendations/{recommendation_id}/dismiss",
    response_model=RecommendationResponse,
    summary="Dismiss recommendation",
)
async def dismiss_recommendation(
    recommendation_id: uuid.UUID,
    body: RecommendationDismissRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationResponse:
    """Dismisses an AI-generated recommendation with justification."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.dismiss_recommendation(
            session=session,
            recommendation_id=recommendation_id,
            dismiss_req=body,
            actor=user_identifier,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/recommendations/{recommendation_id}/snooze",
    response_model=RecommendationResponse,
    summary="Snooze recommendation for N hours",
)
async def snooze_recommendation(
    recommendation_id: uuid.UUID,
    body: RecommendationSnoozeRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecommendationResponse:
    """Snoozes an alert recommendation for a specified number of hours."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.snooze_recommendation(
            session=session,
            recommendation_id=recommendation_id,
            snooze_req=body,
            actor=user_identifier,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
