"""API Endpoints for Post-Mitigation Outcomes and User Feedback."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.outcome import (
    FeedbackCreate,
    FeedbackResponse,
    OutcomeCreate,
    OutcomeResponse,
)
from app.services.agent_service import AgentService
from app.services.auth_service import get_current_user

router = APIRouter(tags=["outcomes"])


@router.post(
    "/risks/{risk_id}/outcome",
    response_model=OutcomeResponse,
    summary="Record post-mitigation outcome for a risk",
)
async def record_risk_outcome(
    risk_id: uuid.UUID,
    body: OutcomeCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OutcomeResponse:
    """Records whether the risk was successfully avoided or mitigated (Yes/Partially/No/Not sure)."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.record_outcome(
            session=session,
            risk_event_id=risk_id,
            outcome_data=body,
            actor=user_identifier,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/risks/{risk_id}/feedback",
    response_model=FeedbackResponse,
    summary="Submit user feedback on risk relevance & accuracy",
)
async def submit_risk_feedback(
    risk_id: uuid.UUID,
    body: FeedbackCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FeedbackResponse:
    """Submits user rating and feedback on alert relevance and analysis quality."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.record_feedback(
            session=session,
            risk_event_id=risk_id,
            feedback_data=body,
            actor=user_identifier,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
