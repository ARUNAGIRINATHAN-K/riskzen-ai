"""API Endpoints for Mitigation Action Item Tracking."""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.action import ActionListResponse, ActionResponse, ActionUpdate
from app.services.agent_service import AgentService
from app.services.auth_service import get_current_user

router = APIRouter(tags=["actions"])


@router.get(
    "/projects/{project_id}/actions",
    response_model=ActionListResponse,
    summary="List mitigation actions for a project",
)
async def list_project_actions(
    project_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status", description="pending | in_progress | completed | overdue"),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionListResponse:
    """Retrieves all mitigation action items for a project with status metrics."""
    return await AgentService.list_project_actions(
        session=session, project_id=project_id, status=status_filter
    )


@router.patch(
    "/actions/{action_id}",
    response_model=ActionResponse,
    summary="Update an action item",
)
async def update_action_item(
    action_id: uuid.UUID,
    body: ActionUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionResponse:
    """Updates action details, assignee owner, due date, or status."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.update_action(
            session=session, action_id=action_id, update_data=body, actor=user_identifier
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/actions/{action_id}/complete",
    response_model=ActionResponse,
    summary="Mark action item complete",
)
async def complete_action_item(
    action_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ActionResponse:
    """Marks an action item as completed and records audit trail."""
    try:
        user_identifier = getattr(current_user, "email", "user")
        return await AgentService.complete_action(
            session=session, action_id=action_id, actor=user_identifier
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
