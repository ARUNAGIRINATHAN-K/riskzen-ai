"""API Endpoints for Risk Threshold Management."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.threshold import RiskThresholdsResponse, RiskThresholdUpdate
from app.services.auth_service import get_current_user
from app.services.risk_engine_service import RiskEngineService

router = APIRouter(tags=["thresholds"])


@router.get(
    "/projects/{project_id}/thresholds",
    response_model=RiskThresholdsResponse,
    summary="Get project risk thresholds",
)
async def get_project_thresholds(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskThresholdsResponse:
    """Retrieves all effective risk threshold values configured for a project."""
    return await RiskEngineService.get_thresholds(session, project_id)


@router.put(
    "/projects/{project_id}/thresholds",
    response_model=RiskThresholdsResponse,
    summary="Update project risk thresholds",
)
async def update_project_thresholds(
    project_id: uuid.UUID,
    updates: RiskThresholdUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskThresholdsResponse:
    """Updates custom risk evaluation thresholds for a project."""
    try:
        return await RiskEngineService.update_thresholds(
            session=session,
            project_id=project_id,
            threshold_updates=updates.thresholds,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update thresholds: {str(e)}",
        )
