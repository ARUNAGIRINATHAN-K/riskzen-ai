"""API Endpoints for Risk Detection Engine and Risk Management."""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.risk import RiskCategory, RiskSeverity, RiskStatus
from app.models.user import User
from app.schemas.risk import (
    RiskDetailResponse,
    RiskEvaluationResponse,
    RiskEventResponse,
    RiskStatusUpdate,
    RiskSummaryResponse,
)
from app.services.auth_service import get_current_user
from app.services.risk_engine_service import RiskEngineService

router = APIRouter(tags=["risks"])


@router.post(
    "/projects/{project_id}/evaluate",
    response_model=RiskEvaluationResponse,
    summary="Trigger deterministic risk detection evaluation",
)
async def evaluate_project_risks(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskEvaluationResponse:
    """Executes the deterministic 7-category risk detection engine on the project."""
    try:
        return await RiskEngineService.evaluate_project(session, project_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk evaluation failed: {str(e)}",
        )


@router.get(
    "/projects/{project_id}/risks",
    response_model=List[RiskEventResponse],
    summary="List risk events for a project",
)
async def list_risks(
    project_id: uuid.UUID,
    category: Optional[RiskCategory] = Query(None, description="Filter by risk category"),
    severity: Optional[RiskSeverity] = Query(None, description="Filter by risk severity"),
    status_filter: Optional[RiskStatus] = Query(None, alias="status", description="Filter by risk status"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[RiskEventResponse]:
    """Retrieves all risk events detected for a project with optional filters."""
    return await RiskEngineService.list_project_risks(
        session=session,
        project_id=project_id,
        category=category,
        severity=severity,
        status=status_filter,
    )


@router.get(
    "/projects/{project_id}/risk-summary",
    response_model=RiskSummaryResponse,
    summary="Get project risk summary and category scores",
)
async def get_risk_summary(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskSummaryResponse:
    """Retrieves high-level risk metrics, propensity scores, and active risk counts."""
    return await RiskEngineService.get_project_risk_summary(session, project_id)


@router.get(
    "/projects/{project_id}/risks/{risk_id}",
    response_model=RiskDetailResponse,
    summary="Get risk event details with evidence and history",
)
async def get_risk_detail(
    project_id: uuid.UUID,
    risk_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskDetailResponse:
    """Retrieves full risk event details including all signals, evidence trails, and audit history."""
    detail = await RiskEngineService.get_risk_detail(session, risk_id)
    if not detail or detail.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk event with ID {risk_id} not found in this project.",
        )
    return detail


@router.patch(
    "/projects/{project_id}/risks/{risk_id}/status",
    response_model=RiskDetailResponse,
    summary="Update risk status (mitigate, dismiss, resolve, close)",
)
async def update_risk_status(
    project_id: uuid.UUID,
    risk_id: uuid.UUID,
    update_data: RiskStatusUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RiskDetailResponse:
    """Transitions the lifecycle status of a risk event and records audit trail."""
    user_identifier = getattr(current_user, "email", "user")
    updated = await RiskEngineService.update_risk_status(
        session=session,
        risk_id=risk_id,
        update_data=update_data,
        changed_by=user_identifier,
    )
    if not updated or updated.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk event with ID {risk_id} not found in this project.",
        )
    return updated
