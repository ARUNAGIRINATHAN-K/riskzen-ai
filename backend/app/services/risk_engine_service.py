"""Risk Engine Service.

Orchestrates deterministic rule evaluation, risk event deduplication,
scoring aggregation, state persistence, history tracking, and threshold management.
"""
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.dependency import Dependency
from app.models.milestone import Milestone
from app.models.project import Project, ProjectMember
from app.models.risk import (
    Evidence,
    RiskCategory,
    RiskEvent,
    RiskHistory,
    RiskSeverity,
    RiskSignal as RiskSignalModel,
    RiskStatus,
    RiskThreshold,
)
from app.models.work_item import WorkItem
from app.risk_engine.base_rule import ProjectState, RiskSignal
from app.risk_engine.rules import get_all_rules
from app.risk_engine.scoring import calculate_project_risk_score
from app.risk_engine.thresholds import get_merged_thresholds
from app.schemas.risk import (
    EvidenceResponse,
    RiskCategorySummary,
    RiskDetailResponse,
    RiskEvaluationResponse,
    RiskEventResponse,
    RiskHistoryResponse,
    RiskSignalResponse,
    RiskStatusUpdate,
    RiskSummaryResponse,
)
from app.schemas.threshold import RiskThresholdItem, RiskThresholdsResponse


class RiskEngineService:
    """Service handling risk evaluation, query, status workflows, and thresholds."""

    @classmethod
    async def evaluate_project(
        cls, session: AsyncSession, project_id: uuid.UUID
    ) -> RiskEvaluationResponse:
        """Runs the deterministic risk detection engine on a project."""
        # 1. Fetch project with all related entities
        proj_stmt = select(Project).where(Project.id == project_id)
        proj_res = await session.execute(proj_stmt)
        project = proj_res.scalar_one_or_none()
        if not project:
            raise ValueError(f"Project with ID {project_id} not found.")

        # Milestones
        m_stmt = select(Milestone).where(Milestone.project_id == project_id)
        m_res = await session.execute(m_stmt)
        milestones = list(m_res.scalars().all())

        # Work Items
        w_stmt = select(WorkItem).where(WorkItem.project_id == project_id)
        w_res = await session.execute(w_stmt)
        work_items = list(w_res.scalars().all())

        # Dependencies
        d_stmt = select(Dependency).where(
            (Dependency.source_item_id.in_([w.id for w in work_items]))
            | (Dependency.target_item_id.in_([w.id for w in work_items]))
        ) if work_items else select(Dependency).where(False)
        d_res = await session.execute(d_stmt)
        dependencies = list(d_res.scalars().all())

        # Team Members
        mem_stmt = select(ProjectMember).where(ProjectMember.project_id == project_id)
        mem_res = await session.execute(mem_stmt)
        members = list(mem_res.scalars().all())

        # Existing Risk Thresholds
        t_stmt = select(RiskThreshold).where(RiskThreshold.project_id == project_id)
        t_res = await session.execute(t_stmt)
        db_thresholds = {t.name: t.value for t in t_res.scalars().all()}
        merged_thresholds = get_merged_thresholds(db_thresholds)

        # 2. Build In-Memory ProjectState
        state = ProjectState.build(
            project=project,
            milestones=milestones,
            work_items=work_items,
            dependencies=dependencies,
            members=members,
            thresholds=merged_thresholds,
            evaluation_time=datetime.now(timezone.utc),
        )

        # 3. Evaluate all deterministic rules (100% LLM-free)
        rules = get_all_rules()
        detected_signals: List[RiskSignal] = []
        for rule in rules:
            try:
                rule_signals = rule.evaluate(state)
                detected_signals.extend(rule_signals)
            except Exception as ex:
                # Rule execution isolation: prevent one failing rule from breaking evaluation
                continue

        # 4. Calculate overall & category risk scores
        score_result = calculate_project_risk_score(
            signals=detected_signals,
            data_quality_score=getattr(project, "data_quality_score", None),
        )

        # 5. Fetch existing active risk events for deduplication
        existing_events_stmt = (
            select(RiskEvent)
            .where(RiskEvent.project_id == project_id)
            .options(
                selectinload(RiskEvent.signals).selectinload(RiskSignalModel.evidence),
                selectinload(RiskEvent.history),
            )
        )
        existing_res = await session.execute(existing_events_stmt)
        existing_events = list(existing_res.scalars().all())
        existing_map: Dict[str, RiskEvent] = {
            f"{e.category.value}:{e.signal_type}:{e.affected_milestone_id or 'none'}": e
            for e in existing_events
        }

        active_keys = set()
        created_events_count = 0
        updated_events_count = 0

        # 6. Upsert detected risk events and signals
        for sig in detected_signals:
            dedup_key = f"{sig.category.value}:{sig.signal_type}:{sig.affected_milestone_id or 'none'}"
            active_keys.add(dedup_key)

            existing_event = existing_map.get(dedup_key)

            if existing_event:
                # Update existing event if active or new
                if existing_event.status in (RiskStatus.NEW, RiskStatus.ACTIVE):
                    old_score = existing_event.propensity_score
                    old_sev = existing_event.severity

                    existing_event.title = sig.title
                    existing_event.description = sig.description
                    existing_event.severity = sig.severity
                    existing_event.propensity_score = sig.score
                    existing_event.confidence = sig.confidence
                    existing_event.status = RiskStatus.ACTIVE
                    existing_event.updated_at = datetime.now(timezone.utc)

                    # Append history record
                    history_entry = RiskHistory(
                        risk_event_id=existing_event.id,
                        previous_status=existing_event.status,
                        new_status=existing_event.status,
                        changed_by="risk_engine",
                        reason=(
                            f"Deterministic re-evaluation: severity={sig.severity.value}, "
                            f"score={sig.score:.2f} (prev: {old_sev.value if old_sev else 'none'}, {old_score:.2f})"
                        ),
                    )
                    session.add(history_entry)
                    updated_events_count += 1
            else:
                # Create brand new RiskEvent
                new_event = RiskEvent(
                    project_id=project_id,
                    category=sig.category,
                    severity=sig.severity,
                    propensity_score=sig.score,
                    confidence=sig.confidence,
                    status=RiskStatus.NEW,
                    title=sig.title,
                    description=sig.description,
                    signal_type=sig.signal_type,
                    affected_milestone_id=uuid.UUID(sig.affected_milestone_id) if sig.affected_milestone_id else None,
                    raw_metrics=sig.raw_metrics,
                )
                session.add(new_event)
                await session.flush()  # Generate new_event.id

                # Create RiskSignalModel
                sig_model = RiskSignalModel(
                    risk_event_id=new_event.id,
                    rule_id=sig.rule_id,
                    signal_type=sig.signal_type,
                    severity=sig.severity,
                    score=sig.score,
                    confidence=sig.confidence,
                    description=sig.description,
                    metadata_json=sig.raw_metrics,
                )
                session.add(sig_model)
                await session.flush()

                # Create Evidence records
                for ev_item in sig.evidence:
                    ev_model = Evidence(
                        signal_id=sig_model.id,
                        source_type=ev_item.source_type,
                        source_id=ev_item.source_id,
                        description=ev_item.description,
                        data_payload=ev_item.metadata,
                    )
                    session.add(ev_model)

                # Record Initial History
                hist = RiskHistory(
                    risk_event_id=new_event.id,
                    previous_status=None,
                    new_status=RiskStatus.NEW,
                    changed_by="risk_engine",
                    reason=f"Detected by rule {sig.rule_id}: {sig.title}",
                )
                session.add(hist)
                created_events_count += 1

        # 7. Auto-resolve events that no longer trigger
        resolved_count = 0
        for key, event in existing_map.items():
            if key not in active_keys and event.status in (RiskStatus.NEW, RiskStatus.ACTIVE):
                old_st = event.status
                event.status = RiskStatus.RESOLVED
                event.resolved_at = datetime.now(timezone.utc)
                event.updated_at = datetime.now(timezone.utc)
                
                hist = RiskHistory(
                    risk_event_id=event.id,
                    previous_status=old_st,
                    new_status=RiskStatus.RESOLVED,
                    changed_by="risk_engine",
                    reason="Risk condition no longer detected during re-evaluation.",
                )
                session.add(hist)
                resolved_count += 1

        # 8. Update Project risk metadata
        proj_settings = project.settings or {}
        proj_settings["last_evaluated_at"] = datetime.now(timezone.utc).isoformat()
        proj_settings["overall_risk_score"] = score_result.overall_score
        proj_settings["overall_risk_level"] = score_result.overall_severity.value
        proj_settings["risk_confidence"] = score_result.confidence
        project.settings = proj_settings

        await session.commit()

        # Build response
        category_summaries = {
            cat_str: RiskCategorySummary(
                category=cat_str,
                score=cat_res.score,
                severity=cat_res.severity,
                signal_count=cat_res.signal_count,
            )
            for cat_str, cat_res in score_result.category_scores.items()
        }

        return RiskEvaluationResponse(
            project_id=project_id,
            evaluation_time=state.evaluation_time,
            overall_score=score_result.overall_score,
            overall_severity=score_result.overall_severity,
            confidence=score_result.confidence,
            category_scores=category_summaries,
            total_signals=score_result.total_signals,
            created_risks_count=created_events_count,
            updated_risks_count=updated_events_count,
            resolved_risks_count=resolved_count,
        )

    @classmethod
    async def list_project_risks(
        cls,
        session: AsyncSession,
        project_id: uuid.UUID,
        category: Optional[RiskCategory] = None,
        severity: Optional[RiskSeverity] = None,
        status: Optional[RiskStatus] = None,
    ) -> List[RiskEventResponse]:
        """Lists risk events for a project with optional filtering."""
        query = (
            select(RiskEvent)
            .where(RiskEvent.project_id == project_id)
            .options(
                selectinload(RiskEvent.signals).selectinload(RiskSignalModel.evidence)
            )
            .order_by(RiskEvent.propensity_score.desc(), RiskEvent.created_at.desc())
        )

        if category:
            query = query.where(RiskEvent.category == category)
        if severity:
            query = query.where(RiskEvent.severity == severity)
        if status:
            query = query.where(RiskEvent.status == status)

        res = await session.execute(query)
        events = res.scalars().all()

        results = []
        for e in events:
            sig_responses = [
                RiskSignalResponse(
                    id=s.id,
                    rule_id=s.rule_id,
                    signal_type=s.signal_type,
                    severity=s.severity,
                    score=s.score,
                    confidence=s.confidence,
                    description=s.description,
                    metadata_json=s.metadata_json,
                    evidence=[
                        EvidenceResponse(
                            id=ev.id,
                            source_type=ev.source_type,
                            source_id=ev.source_id,
                            description=ev.description,
                            data_payload=ev.data_payload,
                            created_at=ev.created_at,
                        )
                        for ev in s.evidence
                    ],
                    created_at=s.created_at,
                )
                for s in e.signals
            ]

            results.append(
                RiskEventResponse(
                    id=e.id,
                    project_id=e.project_id,
                    category=e.category,
                    severity=e.severity,
                    propensity_score=e.propensity_score,
                    confidence=e.confidence,
                    status=e.status,
                    title=e.title,
                    description=e.description,
                    signal_type=e.signal_type,
                    affected_milestone_id=e.affected_milestone_id,
                    raw_metrics=e.raw_metrics,
                    signals=sig_responses,
                    created_at=e.created_at,
                    updated_at=e.updated_at,
                    resolved_at=e.resolved_at,
                )
            )

        return results

    @classmethod
    async def get_risk_detail(
        cls, session: AsyncSession, risk_id: uuid.UUID
    ) -> Optional[RiskDetailResponse]:
        """Gets complete details of a specific risk event including evidence and audit history."""
        query = (
            select(RiskEvent)
            .where(RiskEvent.id == risk_id)
            .options(
                selectinload(RiskEvent.signals).selectinload(RiskSignalModel.evidence),
                selectinload(RiskEvent.history),
            )
        )
        res = await session.execute(query)
        e = res.scalar_one_or_none()
        if not e:
            return None

        sig_responses = [
            RiskSignalResponse(
                id=s.id,
                rule_id=s.rule_id,
                signal_type=s.signal_type,
                severity=s.severity,
                score=s.score,
                confidence=s.confidence,
                description=s.description,
                metadata_json=s.metadata_json,
                evidence=[
                    EvidenceResponse(
                        id=ev.id,
                        source_type=ev.source_type,
                        source_id=ev.source_id,
                        description=ev.description,
                        data_payload=ev.data_payload,
                        created_at=ev.created_at,
                    )
                    for ev in s.evidence
                ],
                created_at=s.created_at,
            )
            for s in e.signals
        ]

        history_responses = [
            RiskHistoryResponse(
                id=h.id,
                risk_event_id=h.risk_event_id,
                previous_status=h.previous_status,
                new_status=h.new_status,
                changed_by=h.changed_by,
                reason=h.reason,
                created_at=h.created_at,
            )
            for h in sorted(e.history, key=lambda x: x.created_at, reverse=True)
        ]

        return RiskDetailResponse(
            id=e.id,
            project_id=e.project_id,
            category=e.category,
            severity=e.severity,
            propensity_score=e.propensity_score,
            confidence=e.confidence,
            status=e.status,
            title=e.title,
            description=e.description,
            signal_type=e.signal_type,
            affected_milestone_id=e.affected_milestone_id,
            raw_metrics=e.raw_metrics,
            signals=sig_responses,
            history=history_responses,
            created_at=e.created_at,
            updated_at=e.updated_at,
            resolved_at=e.resolved_at,
        )

    @classmethod
    async def update_risk_status(
        cls,
        session: AsyncSession,
        risk_id: uuid.UUID,
        update_data: RiskStatusUpdate,
        changed_by: str = "user",
    ) -> Optional[RiskDetailResponse]:
        """Updates the status of a risk event (e.g. mitigated, dismissed) and writes audit history."""
        query = (
            select(RiskEvent)
            .where(RiskEvent.id == risk_id)
            .options(
                selectinload(RiskEvent.signals).selectinload(RiskSignalModel.evidence),
                selectinload(RiskEvent.history),
            )
        )
        res = await session.execute(query)
        event = res.scalar_one_or_none()
        if not event:
            return None

        old_status = event.status
        new_status = update_data.status

        event.status = new_status
        event.updated_at = datetime.now(timezone.utc)
        if new_status in (RiskStatus.RESOLVED, RiskStatus.CLOSED, RiskStatus.DISMISSED):
            event.resolved_at = datetime.now(timezone.utc)

        # Audit history entry
        history_entry = RiskHistory(
            risk_event_id=event.id,
            previous_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=update_data.reason or f"Status changed from {old_status.value} to {new_status.value}",
        )
        session.add(history_entry)
        await session.commit()

        return await cls.get_risk_detail(session, risk_id)

    @classmethod
    async def get_project_risk_summary(
        cls, session: AsyncSession, project_id: uuid.UUID
    ) -> RiskSummaryResponse:
        """Computes current project risk summary and aggregated category metrics."""
        events_stmt = select(RiskEvent).where(
            RiskEvent.project_id == project_id,
            RiskEvent.status.in_([RiskStatus.NEW, RiskStatus.ACTIVE]),
        )
        res = await session.execute(events_stmt)
        active_events = list(res.scalars().all())

        by_cat: Dict[str, int] = defaultdict(int)
        by_sev: Dict[str, int] = defaultdict(int)
        cat_scores: Dict[str, RiskCategorySummary] = {}

        for cat in RiskCategory:
            cat_events = [e for e in active_events if e.category == cat]
            by_cat[cat.value] = len(cat_events)
            cat_score = max([e.propensity_score for e in cat_events], default=0.0)
            
            # Severity for category
            if cat_score >= 0.70:
                c_sev = RiskSeverity.CRITICAL
            elif cat_score >= 0.45:
                c_sev = RiskSeverity.HIGH
            elif cat_score >= 0.20:
                c_sev = RiskSeverity.MEDIUM
            else:
                c_sev = RiskSeverity.LOW

            cat_scores[cat.value] = RiskCategorySummary(
                category=cat.value,
                score=round(cat_score, 3),
                severity=c_sev,
                signal_count=len(cat_events),
            )

        for e in active_events:
            by_sev[e.severity.value] += 1

        overall_score = sum(c.score for c in cat_scores.values()) / 7.0
        if any(e.severity == RiskSeverity.CRITICAL for e in active_events):
            overall_sev = RiskSeverity.CRITICAL
        elif any(e.severity == RiskSeverity.HIGH for e in active_events):
            overall_sev = RiskSeverity.HIGH
        elif overall_score >= 0.20:
            overall_sev = RiskSeverity.MEDIUM
        else:
            overall_sev = RiskSeverity.LOW

        return RiskSummaryResponse(
            project_id=project_id,
            overall_score=round(overall_score, 3),
            overall_severity=overall_sev,
            confidence=0.85,
            total_active_risks=len(active_events),
            risks_by_category=dict(by_cat),
            risks_by_severity=dict(by_sev),
            category_summaries=cat_scores,
            last_evaluated_at=datetime.now(timezone.utc),
        )

    @classmethod
    async def get_thresholds(
        cls, session: AsyncSession, project_id: uuid.UUID
    ) -> RiskThresholdsResponse:
        """Returns all effective risk thresholds for a project."""
        t_stmt = select(RiskThreshold).where(RiskThreshold.project_id == project_id)
        res = await session.execute(t_stmt)
        db_thresholds = {t.name: t.value for t in res.scalars().all()}
        merged = get_merged_thresholds(db_thresholds)

        items = [
            RiskThresholdItem(
                name=k,
                value=v,
                description=f"Configurable threshold for {k.replace('_', ' ')}",
            )
            for k, v in merged.items()
        ]
        return RiskThresholdsResponse(project_id=project_id, thresholds=items)

    @classmethod
    async def update_thresholds(
        cls, session: AsyncSession, project_id: uuid.UUID, threshold_updates: Dict[str, float]
    ) -> RiskThresholdsResponse:
        """Updates or creates custom thresholds for a project."""
        for name, value in threshold_updates.items():
            stmt = select(RiskThreshold).where(
                RiskThreshold.project_id == project_id,
                RiskThreshold.name == name,
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if existing:
                existing.value = float(value)
            else:
                new_t = RiskThreshold(
                    project_id=project_id,
                    name=name,
                    value=float(value),
                    description=f"Custom threshold for {name}",
                )
                session.add(new_t)

        await session.commit()
        return await cls.get_thresholds(session, project_id)
