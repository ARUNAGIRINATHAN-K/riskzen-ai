"""Agent Investigation & Recommendation Service.

Orchestrates LangGraph workflow execution, recommendation approvals, action item tracking,
and post-mitigation outcome feedback.
"""
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agent.graph import build_investigation_graph
from app.agent.llm import BaseLLMService, get_llm_service
from app.agent.state import InvestigationState
from app.models.audit import AuditLog
from app.models.milestone import Milestone
from app.models.project import Project, ProjectMember
from app.models.recommendation import Action, Outcome, Recommendation
from app.models.risk import RiskCategory, RiskEvent, RiskSeverity, RiskSignal, RiskStatus
from app.models.user import User
from app.models.work_item import WorkItem
from app.schemas.action import (
    ActionCreate,
    ActionListResponse,
    ActionResponse,
    ActionUpdate,
)
from app.schemas.outcome import (
    FeedbackCreate,
    FeedbackResponse,
    OutcomeCreate,
    OutcomeResponse,
)
from app.schemas.recommendation import (
    InvestigationTriggerResponse,
    RecommendationApproveRequest,
    RecommendationDismissRequest,
    RecommendationModifyRequest,
    RecommendationResponse,
    RecommendationSnoozeRequest,
)
from app.utils.logging import get_logger

logger = get_logger("riskzen.services.agent")


class AgentService:
    """Service orchestrating AI agent investigations and PM decision workflows."""

    @classmethod
    async def investigate_risk(
        cls,
        session: AsyncSession,
        risk_event_id: uuid.UUID,
        llm_service: Optional[BaseLLMService] = None,
        actor: str = "system",
    ) -> InvestigationTriggerResponse:
        """Runs the 5-node LangGraph investigation workflow for a specific risk event."""
        llm = llm_service or get_llm_service()

        # 1. Fetch Risk Event with signals
        stmt = (
            select(RiskEvent)
            .where(RiskEvent.id == risk_event_id)
            .options(
                selectinload(RiskEvent.signals),
                selectinload(RiskEvent.recommendations),
            )
        )
        res = await session.execute(stmt)
        risk = res.scalar_one_or_none()
        if not risk:
            raise ValueError(f"Risk event with ID '{risk_event_id}' not found.")

        # 2. Fetch Project Context
        proj_stmt = select(Project).where(Project.id == risk.project_id)
        proj_res = await session.execute(proj_stmt)
        project = proj_res.scalar_one_or_none()

        w_stmt = select(WorkItem).where(WorkItem.project_id == risk.project_id)
        w_res = await session.execute(w_stmt)
        work_items = list(w_res.scalars().all())

        m_stmt = select(Milestone).where(Milestone.project_id == risk.project_id)
        m_res = await session.execute(m_stmt)
        milestones = list(m_res.scalars().all())

        mem_stmt = (
            select(ProjectMember, User)
            .outerjoin(User, ProjectMember.user_id == User.id)
            .where(ProjectMember.project_id == risk.project_id)
        )
        mem_res = await session.execute(mem_stmt)
        members_data = []
        for pm, user in mem_res.all():
            name = user.full_name if user else f"Member ({pm.role})"
            members_data.append({"name": name, "role": pm.role or "Developer"})

        # Build Project Context dict
        now = datetime.now(timezone.utc)
        overdue_count = sum(
            1 for w in work_items
            if w.due_date and w.status.lower() not in ("closed", "done", "completed")
            and (w.due_date.replace(tzinfo=timezone.utc) if w.due_date.tzinfo is None else w.due_date) < now
        )

        project_ctx = {
            "project_name": project.name if project else "Project",
            "total_work_items": len(work_items),
            "overdue_items_count": overdue_count,
            "active_members_count": len(members_data),
            "milestones_summary": [f"{m.title} (due {m.due_date})" for m in milestones],
            "team_members": members_data,
        }

        # 3. Assemble Initial LangGraph State
        signals_data = [
            {
                "rule_id": s.rule_id,
                "signal_type": s.signal_type,
                "severity": s.severity.value,
                "score": s.score,
                "description": s.description,
            }
            for s in risk.signals
        ]

        initial_state: InvestigationState = {
            "risk_event_id": str(risk.id),
            "project_id": str(risk.project_id),
            "risk_title": risk.title,
            "risk_category": risk.category.value,
            "risk_severity": risk.severity.value,
            "affected_milestone_id": str(risk.affected_milestone_id) if risk.affected_milestone_id else None,
            "risk_signals": signals_data,
            "project_context": project_ctx,
            "initial_hypothesis": "",
            "scope_of_investigation": "",
            "key_questions": [],
            "evidence_queries": [risk.title],
            "retrieved_evidence": [],
            "explanation": "",
            "contributing_factors": [],
            "analysis_confidence": 0.85,
            "recommendations": [],
            "quality_check_passed": True,
            "review_feedback": "",
            "hallucination_detected": False,
            "retry_count": 0,
            "error": None,
        }

        # 4. Compile and Run Graph
        graph = build_investigation_graph(session, llm)
        final_state = await graph.ainvoke(initial_state)

        # 5. Persist Recommendations to DB
        created_recs: List[Recommendation] = []
        for rec_item in final_state.get("recommendations", []):
            rec = Recommendation(
                risk_event_id=risk.id,
                action_description=rec_item.get("action_description", ""),
                rationale=rec_item.get("rationale", ""),
                suggested_owner=rec_item.get("suggested_owner"),
                urgency=rec_item.get("urgency", "this_week"),
                status="pending",
            )
            session.add(rec)
            created_recs.append(rec)

        # 6. Update Risk Event metadata
        risk_raw = risk.raw_metrics or {}
        risk_raw["explanation"] = final_state.get("explanation")
        risk_raw["contributing_factors"] = final_state.get("contributing_factors")
        risk_raw["analysis_confidence"] = final_state.get("analysis_confidence")
        risk_raw["investigated_at"] = datetime.now(timezone.utc).isoformat()
        risk.raw_metrics = risk_raw
        risk.confidence = float(final_state.get("analysis_confidence", 0.85))
        risk.updated_at = datetime.now(timezone.utc)

        # 7. Write Audit Log
        audit = AuditLog(
            project_id=risk.project_id,
            event_type="risk_investigated",
            entity_type="risk_event",
            entity_id=risk.id,
            actor=actor,
            details={
                "risk_title": risk.title,
                "recommendations_generated": len(created_recs),
                "confidence": final_state.get("analysis_confidence"),
                "quality_check_passed": final_state.get("quality_check_passed"),
            },
        )
        session.add(audit)
        await session.commit()

        # Refresh created recommendations for response
        rec_responses = []
        for r in created_recs:
            await session.refresh(r)
            rec_responses.append(RecommendationResponse.model_validate(r))

        return InvestigationTriggerResponse(
            risk_event_id=risk.id,
            project_id=risk.project_id,
            status="completed",
            explanation=final_state.get("explanation"),
            contributing_factors_count=len(final_state.get("contributing_factors", [])),
            recommendations_count=len(created_recs),
            recommendations=rec_responses,
            confidence=float(final_state.get("analysis_confidence", 0.85)),
            quality_check_passed=bool(final_state.get("quality_check_passed", True)),
        )

    @classmethod
    async def trigger_investigations_for_material_risks(
        cls,
        session: AsyncSession,
        project_id: uuid.UUID,
        llm_service: Optional[BaseLLMService] = None,
    ) -> List[InvestigationTriggerResponse]:
        """Automatically triggers AI investigation for newly detected HIGH or CRITICAL risks."""
        stmt = (
            select(RiskEvent)
            .where(
                RiskEvent.project_id == project_id,
                RiskEvent.status.in_([RiskStatus.NEW, RiskStatus.ACTIVE]),
                (RiskEvent.severity.in_([RiskSeverity.HIGH, RiskSeverity.CRITICAL]))
                | (RiskEvent.propensity_score >= 0.60),
            )
            .options(selectinload(RiskEvent.recommendations))
        )
        res = await session.execute(stmt)
        risks = res.scalars().all()

        investigations: List[InvestigationTriggerResponse] = []
        for risk in risks:
            # If no pending or approved recommendations exist yet
            if not risk.recommendations:
                try:
                    inv_resp = await cls.investigate_risk(
                        session=session,
                        risk_event_id=risk.id,
                        llm_service=llm_service,
                        actor="auto_trigger",
                    )
                    investigations.append(inv_resp)
                except Exception as exc:
                    logger.error("Auto investigation failed for risk", risk_id=str(risk.id), error=str(exc))

        return investigations

    @classmethod
    async def list_risk_recommendations(
        cls, session: AsyncSession, risk_event_id: uuid.UUID
    ) -> List[RecommendationResponse]:
        """Lists all recommendations for a given risk event."""
        stmt = (
            select(Recommendation)
            .where(Recommendation.risk_event_id == risk_event_id)
            .order_by(Recommendation.created_at.asc())
        )
        res = await session.execute(stmt)
        recs = res.scalars().all()
        return [RecommendationResponse.model_validate(r) for r in recs]

    @classmethod
    async def approve_recommendation(
        cls,
        session: AsyncSession,
        recommendation_id: uuid.UUID,
        approve_req: RecommendationApproveRequest,
        actor: str = "user",
    ) -> ActionResponse:
        """Approves a recommendation, converts it into an Action record, and logs audit decision."""
        rec = await session.get(Recommendation, recommendation_id)
        if not rec:
            raise ValueError(f"Recommendation '{recommendation_id}' not found.")

        risk = await session.get(RiskEvent, rec.risk_event_id)
        project_id = risk.project_id if risk else uuid.uuid4()

        # Update recommendation status
        rec.status = "approved"
        rec.decided_at = datetime.now(timezone.utc)
        rec.decision_reason = "Approved by project lead"

        # Determine target due date
        action_due = None
        if approve_req.due_date:
            try:
                action_due = datetime.strptime(approve_req.due_date, "%Y-%m-%d").date()
            except ValueError:
                action_due = date.today() + timedelta(days=7)
        else:
            days_offset = 1 if rec.urgency == "immediate" else (3 if rec.urgency == "today" else 7)
            action_due = date.today() + timedelta(days=days_offset)

        # Create Action item
        owner_name = approve_req.owner or rec.suggested_owner or "Project Lead"
        action = Action(
            recommendation_id=rec.id,
            project_id=project_id,
            description=rec.action_description,
            owner=owner_name,
            due_date=action_due,
            status="pending",
        )
        session.add(action)

        # Log to AuditLog
        audit = AuditLog(
            project_id=project_id,
            event_type="recommendation_approved",
            entity_type="recommendation",
            entity_id=rec.id,
            actor=actor,
            details={
                "action_description": rec.action_description,
                "owner": owner_name,
                "due_date": str(action_due),
            },
        )
        session.add(audit)
        await session.commit()
        await session.refresh(action)

        return ActionResponse.model_validate(action)

    @classmethod
    async def modify_recommendation(
        cls,
        session: AsyncSession,
        recommendation_id: uuid.UUID,
        modify_req: RecommendationModifyRequest,
        actor: str = "user",
    ) -> ActionResponse:
        """Modifies recommendation parameters and creates an Action record."""
        rec = await session.get(Recommendation, recommendation_id)
        if not rec:
            raise ValueError(f"Recommendation '{recommendation_id}' not found.")

        risk = await session.get(RiskEvent, rec.risk_event_id)
        project_id = risk.project_id if risk else uuid.uuid4()

        rec.status = "modified"
        rec.action_description = modify_req.action_description
        if modify_req.rationale:
            rec.rationale = modify_req.rationale
        rec.decided_at = datetime.now(timezone.utc)
        rec.decision_reason = modify_req.reason or "Modified and approved by user"

        action_due = None
        if modify_req.due_date:
            try:
                action_due = datetime.strptime(modify_req.due_date, "%Y-%m-%d").date()
            except ValueError:
                action_due = date.today() + timedelta(days=7)
        else:
            action_due = date.today() + timedelta(days=7)

        action = Action(
            recommendation_id=rec.id,
            project_id=project_id,
            description=modify_req.action_description,
            owner=modify_req.owner,
            due_date=action_due,
            status="pending",
        )
        session.add(action)

        audit = AuditLog(
            project_id=project_id,
            event_type="recommendation_modified",
            entity_type="recommendation",
            entity_id=rec.id,
            actor=actor,
            details={
                "modified_action": modify_req.action_description,
                "owner": modify_req.owner,
                "reason": modify_req.reason,
            },
        )
        session.add(audit)
        await session.commit()
        await session.refresh(action)

        return ActionResponse.model_validate(action)

    @classmethod
    async def dismiss_recommendation(
        cls,
        session: AsyncSession,
        recommendation_id: uuid.UUID,
        dismiss_req: RecommendationDismissRequest,
        actor: str = "user",
    ) -> RecommendationResponse:
        """Dismisses a recommendation with explanation."""
        rec = await session.get(Recommendation, recommendation_id)
        if not rec:
            raise ValueError(f"Recommendation '{recommendation_id}' not found.")

        risk = await session.get(RiskEvent, rec.risk_event_id)
        project_id = risk.project_id if risk else uuid.uuid4()

        rec.status = "dismissed"
        rec.decided_at = datetime.now(timezone.utc)
        rec.decision_reason = dismiss_req.reason

        audit = AuditLog(
            project_id=project_id,
            event_type="recommendation_dismissed",
            entity_type="recommendation",
            entity_id=rec.id,
            actor=actor,
            details={"reason": dismiss_req.reason},
        )
        session.add(audit)
        await session.commit()
        await session.refresh(rec)

        return RecommendationResponse.model_validate(rec)

    @classmethod
    async def snooze_recommendation(
        cls,
        session: AsyncSession,
        recommendation_id: uuid.UUID,
        snooze_req: RecommendationSnoozeRequest,
        actor: str = "user",
    ) -> RecommendationResponse:
        """Snoozes a recommendation for specified hours."""
        rec = await session.get(Recommendation, recommendation_id)
        if not rec:
            raise ValueError(f"Recommendation '{recommendation_id}' not found.")

        risk = await session.get(RiskEvent, rec.risk_event_id)
        project_id = risk.project_id if risk else uuid.uuid4()

        rec.status = "snoozed"
        rec.decided_at = datetime.now(timezone.utc)
        rec.snooze_until = datetime.now(timezone.utc) + timedelta(hours=snooze_req.snooze_hours)
        rec.decision_reason = snooze_req.reason or f"Snoozed for {snooze_req.snooze_hours} hours"

        audit = AuditLog(
            project_id=project_id,
            event_type="recommendation_snoozed",
            entity_type="recommendation",
            entity_id=rec.id,
            actor=actor,
            details={
                "hours": snooze_req.snooze_hours,
                "snooze_until": rec.snooze_until.isoformat(),
            },
        )
        session.add(audit)
        await session.commit()
        await session.refresh(rec)

        return RecommendationResponse.model_validate(rec)

    @classmethod
    async def list_project_actions(
        cls, session: AsyncSession, project_id: uuid.UUID, status: Optional[str] = None
    ) -> ActionListResponse:
        """Lists all mitigation actions for a project with summary counts."""
        stmt = select(Action).where(Action.project_id == project_id)
        if status:
            stmt = stmt.where(Action.status == status)
        stmt = stmt.order_by(Action.created_at.desc())

        res = await session.execute(stmt)
        actions = list(res.scalars().all())

        today = date.today()
        # Mark overdue actions dynamically if past due date and not completed
        for a in actions:
            if a.due_date and a.due_date < today and a.status in ("pending", "in_progress"):
                a.status = "overdue"

        open_c = sum(1 for a in actions if a.status in ("pending", "in_progress"))
        completed_c = sum(1 for a in actions if a.status == "completed")
        overdue_c = sum(1 for a in actions if a.status == "overdue")

        return ActionListResponse(
            project_id=project_id,
            total_actions=len(actions),
            open_actions=open_c,
            completed_actions=completed_c,
            overdue_actions=overdue_c,
            actions=[ActionResponse.model_validate(a) for a in actions],
        )

    @classmethod
    async def update_action(
        cls, session: AsyncSession, action_id: uuid.UUID, update_data: ActionUpdate, actor: str = "user"
    ) -> ActionResponse:
        """Updates action description, owner, due date, or status."""
        action = await session.get(Action, action_id)
        if not action:
            raise ValueError(f"Action '{action_id}' not found.")

        if update_data.description is not None:
            action.description = update_data.description
        if update_data.owner is not None:
            action.owner = update_data.owner
        if update_data.due_date is not None:
            action.due_date = update_data.due_date
        if update_data.status is not None:
            action.status = update_data.status
            if update_data.status == "completed":
                action.completed_at = datetime.now(timezone.utc)

        action.updated_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(action)
        return ActionResponse.model_validate(action)

    @classmethod
    async def complete_action(
        cls, session: AsyncSession, action_id: uuid.UUID, actor: str = "user"
    ) -> ActionResponse:
        """Marks an action item complete."""
        action = await session.get(Action, action_id)
        if not action:
            raise ValueError(f"Action '{action_id}' not found.")

        action.status = "completed"
        action.completed_at = datetime.now(timezone.utc)
        action.updated_at = datetime.now(timezone.utc)

        audit = AuditLog(
            project_id=action.project_id,
            event_type="action_completed",
            entity_type="action",
            entity_id=action.id,
            actor=actor,
            details={"description": action.description},
        )
        session.add(audit)
        await session.commit()
        await session.refresh(action)
        return ActionResponse.model_validate(action)

    @classmethod
    async def record_outcome(
        cls,
        session: AsyncSession,
        risk_event_id: uuid.UUID,
        outcome_data: OutcomeCreate,
        actor: str = "user",
    ) -> OutcomeResponse:
        """Records post-mitigation outcome rating for a risk event."""
        risk = await session.get(RiskEvent, risk_event_id)
        if not risk:
            raise ValueError(f"Risk event '{risk_event_id}' not found.")

        # Check existing outcome
        stmt = select(Outcome).where(Outcome.risk_event_id == risk_event_id)
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            existing.result = outcome_data.result
            existing.feedback_comment = outcome_data.feedback_comment
            existing.recorded_at = datetime.now(timezone.utc)
            outcome_obj = existing
        else:
            outcome_obj = Outcome(
                risk_event_id=risk_event_id,
                result=outcome_data.result,
                feedback_comment=outcome_data.feedback_comment,
            )
            session.add(outcome_obj)

        audit = AuditLog(
            project_id=risk.project_id,
            event_type="outcome_recorded",
            entity_type="risk_event",
            entity_id=risk_event_id,
            actor=actor,
            details={
                "result": outcome_data.result,
                "comment": outcome_data.feedback_comment,
            },
        )
        session.add(audit)
        await session.commit()
        await session.refresh(outcome_obj)

        return OutcomeResponse.model_validate(outcome_obj)

    @classmethod
    async def record_feedback(
        cls,
        session: AsyncSession,
        risk_event_id: uuid.UUID,
        feedback_data: FeedbackCreate,
        actor: str = "user",
    ) -> FeedbackResponse:
        """Records user feedback rating on risk relevance and accuracy."""
        risk = await session.get(RiskEvent, risk_event_id)
        if not risk:
            raise ValueError(f"Risk event '{risk_event_id}' not found.")

        # Store feedback in risk raw_metrics
        meta = risk.raw_metrics or {}
        feedbacks = meta.get("user_feedback", [])
        feedback_record = {
            "rating": feedback_data.rating,
            "relevance": feedback_data.relevance,
            "comment": feedback_data.comment,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
        }
        feedbacks.append(feedback_record)
        meta["user_feedback"] = feedbacks
        risk.raw_metrics = meta
        risk.updated_at = datetime.now(timezone.utc)

        audit = AuditLog(
            project_id=risk.project_id,
            event_type="risk_feedback_submitted",
            entity_type="risk_event",
            entity_id=risk_event_id,
            actor=actor,
            details=feedback_record,
        )
        session.add(audit)
        await session.commit()

        return FeedbackResponse(
            risk_event_id=risk_event_id,
            rating=feedback_data.rating,
            relevance=feedback_data.relevance,
            comment=feedback_data.comment,
            recorded_at=datetime.now(timezone.utc),
        )
