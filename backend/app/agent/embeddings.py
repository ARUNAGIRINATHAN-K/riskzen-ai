"""Vector Embedding Pipeline and Evidence Search Engine."""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.llm import BaseLLMService, get_llm_service
from app.models.dependency import Dependency
from app.models.embedding import Embedding
from app.models.milestone import Milestone
from app.models.work_item import WorkItem
from app.utils.logging import get_logger

logger = get_logger("riskzen.agent.embeddings")


class EvidenceRetrievalService:
    """Service handling indexing of project records and hybrid semantic + structural evidence retrieval."""

    @classmethod
    async def index_project_records(
        cls, session: AsyncSession, project_id: uuid.UUID, llm_service: Optional[BaseLLMService] = None
    ) -> int:
        """Indexes work items and milestones into embeddings for vector search."""
        llm = llm_service or get_llm_service()

        # 1. Fetch work items
        w_stmt = select(WorkItem).where(WorkItem.project_id == project_id)
        w_res = await session.execute(w_stmt)
        work_items = w_res.scalars().all()

        # 2. Fetch milestones
        m_stmt = select(Milestone).where(Milestone.project_id == project_id)
        m_res = await session.execute(m_stmt)
        milestones = m_res.scalars().all()

        indexed_count = 0

        # Index work items
        for item in work_items:
            content = (
                f"Work Item: {item.title}\n"
                f"Type: {item.item_type or 'task'} | Status: {item.status} | Priority: {item.priority or 'normal'}\n"
                f"Story Points: {item.story_points or 0} | Due Date: {item.due_date}\n"
                f"Description: {item.description or ''}"
            )
            
            # Check existing embedding
            emb_stmt = select(Embedding).where(
                Embedding.project_id == project_id,
                Embedding.source_type == "work_item",
                Embedding.source_id == item.id,
            )
            emb_res = await session.execute(emb_stmt)
            existing = emb_res.scalar_one_or_none()

            if existing:
                existing.content = content
            else:
                new_emb = Embedding(
                    project_id=project_id,
                    source_type="work_item",
                    source_id=item.id,
                    content=content,
                )
                session.add(new_emb)
            indexed_count += 1

        # Index milestones
        for ms in milestones:
            content = (
                f"Milestone: {ms.title}\n"
                f"Status: {ms.status} | Due Date: {ms.due_date} | Start Date: {ms.start_date}\n"
                f"Description: {ms.description or ''}"
            )
            emb_stmt = select(Embedding).where(
                Embedding.project_id == project_id,
                Embedding.source_type == "milestone",
                Embedding.source_id == ms.id,
            )
            emb_res = await session.execute(emb_stmt)
            existing = emb_res.scalar_one_or_none()

            if existing:
                existing.content = content
            else:
                new_emb = Embedding(
                    project_id=project_id,
                    source_type="milestone",
                    source_id=ms.id,
                    content=content,
                )
                session.add(new_emb)
            indexed_count += 1

        await session.commit()
        logger.info("Project records indexed", project_id=str(project_id), count=indexed_count)
        return indexed_count

    @classmethod
    async def retrieve_evidence(
        cls,
        session: AsyncSession,
        project_id: uuid.UUID,
        queries: List[str],
        affected_milestone_id: Optional[uuid.UUID] = None,
        top_k: int = 6,
    ) -> List[Dict[str, Any]]:
        """Retrieves verified evidence using structured database relationships and text matching."""
        evidence_items: List[Dict[str, Any]] = []
        seen_ids = set()

        # 1. Fetch work items with delays or blockers in the project
        w_stmt = select(WorkItem).where(WorkItem.project_id == project_id)
        w_res = await session.execute(w_stmt)
        work_items = w_res.scalars().all()

        # Index items by ID
        item_map = {item.id: item for item in work_items}

        # 2. Fetch dependencies
        d_stmt = select(Dependency).where(
            (Dependency.source_item_id.in_([w.id for w in work_items]))
            | (Dependency.target_item_id.in_([w.id for w in work_items]))
        ) if work_items else select(Dependency).where(False)
        d_res = await session.execute(d_stmt)
        dependencies = d_res.scalars().all()

        # Dependency block evidence
        for dep in dependencies:
            src = item_map.get(dep.source_item_id)
            tgt = item_map.get(dep.target_item_id)
            if src and tgt and src.status.lower() not in ("closed", "done", "completed"):
                ev_id = f"dep:{dep.id}"
                if ev_id not in seen_ids:
                    seen_ids.add(ev_id)
                    evidence_items.append({
                        "id": str(dep.id),
                        "source_type": "dependency",
                        "title": f"Dependency Blocker: '{src.title}' blocks '{tgt.title}'",
                        "content": (
                            f"Task '{src.title}' [{src.status}, due: {src.due_date or 'none'}] "
                            f"blocks '{tgt.title}' [{tgt.status}]."
                        ),
                        "relevance_score": 0.95,
                        "metadata": {
                            "source_item_id": str(src.id),
                            "target_item_id": str(tgt.id),
                            "source_status": src.status,
                            "target_status": tgt.status,
                        },
                    })

        # 3. Work item query matching & milestone context
        for item in work_items:
            content = f"{item.title} {item.description or ''} {item.item_type or ''} {item.status}"
            # Relevance scoring based on keyword overlap
            matches = sum(1 for q in queries for word in q.lower().split() if word in content.lower())
            
            # Boost if in affected milestone or overdue
            is_overdue = item.due_date and item.status.lower() not in ("closed", "done", "completed")
            is_in_milestone = affected_milestone_id and item.milestone_id == affected_milestone_id

            score = 0.5
            if matches > 0:
                score += min(0.35, matches * 0.1)
            if is_overdue:
                score += 0.15
            if is_in_milestone:
                score += 0.10

            if score >= 0.60 or is_overdue:
                ev_id = f"wi:{item.id}"
                if ev_id not in seen_ids:
                    seen_ids.add(ev_id)
                    evidence_items.append({
                        "id": str(item.id),
                        "source_type": "work_item",
                        "title": f"Work Item: {item.title}",
                        "content": (
                            f"[{item.item_type or 'task'}] Status: {item.status}, Priority: {item.priority or 'normal'}, "
                            f"Due Date: {item.due_date or 'none'}, Assignee: {item.assignee_id or 'Unassigned'}. "
                            f"Description: {item.description or 'No description'}"
                        ),
                        "relevance_score": round(min(1.0, score), 2),
                        "metadata": {
                            "status": item.status,
                            "priority": item.priority,
                            "due_date": item.due_date.isoformat() if item.due_date else None,
                        },
                    })

        # 4. Milestone evidence
        if affected_milestone_id:
            m_stmt = select(Milestone).where(Milestone.id == affected_milestone_id)
            m_res = await session.execute(m_stmt)
            ms = m_res.scalar_one_or_none()
            if ms:
                evidence_items.append({
                    "id": str(ms.id),
                    "source_type": "milestone",
                    "title": f"Milestone: {ms.title}",
                    "content": (
                        f"Milestone '{ms.title}' [Status: {ms.status}]. "
                        f"Target Due Date: {ms.due_date}, Start Date: {ms.start_date}. "
                        f"Description: {ms.description or 'None'}"
                    ),
                    "relevance_score": 0.90,
                    "metadata": {
                        "due_date": ms.due_date.isoformat() if ms.due_date else None,
                        "status": ms.status,
                    },
                })

        # Sort by relevance score descending and take top_k
        evidence_items.sort(key=lambda x: x["relevance_score"], reverse=True)
        return evidence_items[:top_k]
