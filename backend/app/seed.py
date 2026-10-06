"""Realistic Seed Data Generator for RiskZen.

Simulates a 7-person software engineering team building "NovaPay Mobile Checkout".
Embeds deliberate leading risk indicators:
1. Milestone Schedule Slip (Milestone 2 trajectory lagging)
2. Cascading Dependency Block (Task #105 -> #103 -> #102)
3. Capacity Bottleneck (Alex Chen assigned 42% of critical path tasks)
4. Decision Latency (PR #88 pending review for 6 days)
5. Scope Creep (Unestimated tasks #109, #110 added post-sprint kickoff)
"""

import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.budget import BudgetRecord
from app.models.project import DataSource, Project
from app.models.team import Team, TeamMember
from app.models.work_item import Dependency, Milestone, WorkItem
from app.services.data_quality_service import DataQualityService
from app.services.snapshot_service import SnapshotService
from app.utils.logging import get_logger

logger = get_logger("riskzen.seed")

# Team Roster
TEAM_MEMBERS = [
    {"name": "Alex Chen", "role": "Tech Lead / Backend Senior", "email": "alex.chen@novapay.io", "github": "alexchen"},
    {"name": "Priya Sharma", "role": "Senior Frontend Engineer", "email": "priya.sharma@novapay.io", "github": "priyasharma"},
    {"name": "Marcus Vance", "role": "Backend Engineer", "email": "marcus.vance@novapay.io", "github": "marcusv"},
    {"name": "Elena Rostova", "role": "Mobile Engineer", "email": "elena.rostova@novapay.io", "github": "elenar"},
    {"name": "Dev Patel", "role": "Frontend / UI Engineer", "email": "dev.patel@novapay.io", "github": "devp"},
    {"name": "Sara Lindqvist", "role": "QA / Test Automation Lead", "email": "sara.l@novapay.io", "github": "saral"},
    {"name": "Carlos Mendez", "role": "DevOps Engineer", "email": "carlos.m@novapay.io", "github": "carlosm"},
]

# Milestones definition
SEED_MILESTONES = [
    {
        "external_id": "MS-01",
        "title": "Core Payment Engine & Tokenization",
        "description": "PCI-DSS compliant card vault, webhook idempotency, and tokenization microservice.",
        "target_days_offset": 5,
        "status": "open",
        "completion_percent": 65.0,
    },
    {
        "external_id": "MS-02",
        "title": "Checkout UI & Digital Wallets",
        "description": "React Native modal sheet with Apple Pay, Google Pay, and biometric authentication.",
        "target_days_offset": 18,
        "status": "open",
        "completion_percent": 30.0,
    },
    {
        "external_id": "MS-03",
        "title": "Security Compliance & Load Testing",
        "description": "SOC2 audit logging, 5,000 TPS peak load stress test, and pen-testing sign-off.",
        "target_days_offset": 45,
        "status": "open",
        "completion_percent": 0.0,
    },
]

# Work Items definition with embedded risk patterns
SEED_WORK_ITEMS = [
    {
        "external_id": "NOVA-101",
        "title": "Stripe API v3 Webhook Handler & Idempotency Filter",
        "item_type": "task",
        "status": "in_progress",
        "priority": "high",
        "assignee": "Alex Chen",
        "milestone_ext": "MS-01",
        "due_days_offset": 3,
        "labels": ["backend", "stripe", "payments"],
    },
    {
        "external_id": "NOVA-102",
        "title": "PCI-DSS Vault DB Migration Script & Key Rotation",
        "item_type": "task",
        "status": "in_progress",
        "priority": "critical",
        "assignee": "Marcus Vance",
        "milestone_ext": "MS-01",
        "due_days_offset": 2,
        "labels": ["database", "security", "pci-dss", "blocker"],
    },
    {
        "external_id": "NOVA-103",
        "title": "Tokenized Card Vault Retrieval Micro-Endpoint",
        "item_type": "task",
        "status": "open",
        "priority": "critical",
        "assignee": "Alex Chen",
        "milestone_ext": "MS-01",
        "due_days_offset": 4,
        "labels": ["backend", "security", "blocked"],
        "blocked_by": "NOVA-102",
    },
    {
        "external_id": "NOVA-104",
        "title": "Biometric Authentication Sheet & Apple Pay Sheet UI",
        "item_type": "feature",
        "status": "in_progress",
        "priority": "high",
        "assignee": "Priya Sharma",
        "milestone_ext": "MS-02",
        "due_days_offset": 10,
        "labels": ["frontend", "mobile", "apple-pay"],
    },
    {
        "external_id": "NOVA-105",
        "title": "Apple Pay Session Validation & Crypto Signature Verification",
        "item_type": "feature",
        "status": "open",
        "priority": "critical",
        "assignee": "Alex Chen",
        "milestone_ext": "MS-02",
        "due_days_offset": 12,
        "labels": ["backend", "payments", "blocked"],
        "blocked_by": "NOVA-103",
    },
    {
        "external_id": "NOVA-106",
        "title": "Google Pay Token Payload Parser & Decryptor",
        "item_type": "feature",
        "status": "open",
        "priority": "medium",
        "assignee": "Dev Patel",
        "milestone_ext": "MS-02",
        "due_days_offset": 14,
        "labels": ["frontend", "google-pay"],
    },
    {
        "external_id": "NOVA-107",
        "title": "Reopened: Shopping Cart Summary Desync on Network Retry",
        "item_type": "bug",
        "status": "open",
        "priority": "high",
        "assignee": "Priya Sharma",
        "milestone_ext": "MS-02",
        "due_days_offset": 7,
        "labels": ["bug", "reopened", "cart"],
    },
    {
        "external_id": "NOVA-108",
        "title": "PR #88: Core Payment State Machine Refactoring",
        "item_type": "decision",
        "status": "open",
        "priority": "high",
        "assignee": "Marcus Vance",
        "milestone_ext": "MS-01",
        "due_days_offset": 5,
        "labels": ["pr-review", "decision-latency", "stalled"],
    },
    {
        "external_id": "NOVA-109",
        "title": "Unestimated: Loyalty Points Redemption Widget at Checkout",
        "item_type": "feature",
        "status": "open",
        "priority": "medium",
        "assignee": None,
        "milestone_ext": "MS-02",
        "due_days_offset": None,
        "labels": ["scope-creep", "unestimated", "growth-experiment"],
    },
    {
        "external_id": "NOVA-110",
        "title": "Unestimated: Multi-Currency Dynamic FX Rate Preview",
        "item_type": "feature",
        "status": "open",
        "priority": "medium",
        "assignee": None,
        "milestone_ext": "MS-02",
        "due_days_offset": None,
        "labels": ["scope-creep", "unestimated", "fintech"],
    },
]

# Budget records
SEED_BUDGET = [
    {"period": "2026-10", "category": "Engineering", "planned": 55000.0, "actual": 58500.0},
    {"period": "2026-10", "category": "Cloud Infrastructure", "planned": 7500.0, "actual": 8200.0},
    {"period": "2026-10", "category": "Security Audit", "planned": 12000.0, "actual": 12000.0},
    {"period": "2026-11", "category": "Engineering", "planned": 55000.0, "actual": 0.0},
]


async def seed_database(session: AsyncSession) -> Project:
    """Seed project, data sources, teams, milestones, work items, dependencies, and budget."""
    # 1. Check if seed project already exists
    stmt = select(Project).where(Project.name == "NovaPay — Mobile Checkout Revamp")
    result = await session.execute(stmt)
    existing_project = result.scalar_one_or_none()

    if existing_project:
        logger.info("Seed project already exists", project_id=str(existing_project.id))
        return existing_project

    # 2. Create Project
    now = datetime.now(timezone.utc)
    today = now.date()

    project = Project(
        name="NovaPay — Mobile Checkout Revamp",
        description=(
            "Next-generation mobile checkout experience with 1-click biometric auth, "
            "Apple Pay, Google Pay, and localized zero-trust token storage."
        ),
        project_type="software",
        status="active",
        health="yellow",  # Yellow due to bottleneck developer and blocked critical path
        created_at=now - timedelta(days=21),
        updated_at=now,
    )
    session.add(project)
    await session.flush()

    # 3. Create Data Sources
    github_source = DataSource(
        project_id=project.id,
        source_type="github",
        config={
            "repo": "novapay/checkout-core",
            "branch": "main",
            "track_issues": True,
            "track_pull_requests": True,
            "track_milestones": True,
        },
        status="connected",
        last_synced_at=now - timedelta(minutes=15),
        created_at=now - timedelta(days=21),
    )

    budget_source = DataSource(
        project_id=project.id,
        source_type="csv_budget",
        config={
            "filename": "q4-novapay-engineering-budget.csv",
            "currency": "USD",
            "budget_cap": 125000.0,
        },
        status="connected",
        last_synced_at=now - timedelta(hours=2),
        created_at=now - timedelta(days=21),
    )
    session.add_all([github_source, budget_source])

    # 4. Create Team and Team Members
    team = Team(
        project_id=project.id,
        name="Checkout Squad Alpha",
        description="Cross-functional checkout & payment processing delivery pod",
    )
    session.add(team)
    await session.flush()

    for tm in TEAM_MEMBERS:
        member = TeamMember(
            team_id=team.id,
            name=tm["name"],
            role=tm["role"],
            email=tm["email"],
            github_username=tm["github"],
        )
        session.add(member)

    # 5. Create Milestones
    ext_to_milestone: dict[str, Milestone] = {}
    for ms_data in SEED_MILESTONES:
        ms = Milestone(
            project_id=project.id,
            external_id=ms_data["external_id"],
            title=ms_data["title"],
            description=ms_data["description"],
            target_date=today + timedelta(days=ms_data["target_days_offset"]),
            status=ms_data["status"],
            completion_percent=ms_data["completion_percent"],
            created_at=now - timedelta(days=21),
            updated_at=now,
        )
        session.add(ms)
        await session.flush()
        ext_to_milestone[ms_data["external_id"]] = ms

    # 6. Create Work Items
    ext_to_work_item: dict[str, WorkItem] = {}
    for wi_data in SEED_WORK_ITEMS:
        ms = ext_to_milestone.get(wi_data["milestone_ext"])
        due_date = today + timedelta(days=wi_data["due_days_offset"]) if wi_data["due_days_offset"] is not None else None

        wi = WorkItem(
            project_id=project.id,
            milestone_id=ms.id if ms else None,
            external_id=wi_data["external_id"],
            source_type="github",
            title=wi_data["title"],
            description=f"Automated deliverable for {wi_data['title']}",
            status=wi_data["status"],
            priority=wi_data["priority"],
            item_type=wi_data["item_type"],
            assignee=wi_data["assignee"],
            labels=wi_data["labels"],
            due_date=due_date,
            created_at=now - timedelta(days=14),
            updated_at=now - timedelta(days=1),
        )
        session.add(wi)
        await session.flush()
        ext_to_work_item[wi_data["external_id"]] = wi

    # 7. Create Dependencies (Cascading Block: #105 -> #103 -> #102)
    for wi_data in SEED_WORK_ITEMS:
        if "blocked_by" in wi_data:
            source_item = ext_to_work_item.get(wi_data["external_id"])
            blocker_item = ext_to_work_item.get(wi_data["blocked_by"])
            if source_item and blocker_item:
                dep = Dependency(
                    project_id=project.id,
                    source_item_id=source_item.id,
                    target_item_id=blocker_item.id,
                    dependency_type="blocks",
                    status="active",
                    detected_at=now - timedelta(days=5),
                )
                session.add(dep)

    # 8. Create Budget Records
    for b in SEED_BUDGET:
        rec = BudgetRecord(
            project_id=project.id,
            period=b["period"],
            category=b["category"],
            planned_amount=b["planned"],
            actual_amount=b["actual"],
            variance=round(b["actual"] - b["planned"], 2),
            currency="USD",
            source_filename="q4-novapay-engineering-budget.csv",
        )
        session.add(rec)

    await session.commit()
    await session.refresh(project)

    # 9. Evaluate initial Data Quality & Snapshot
    await DataQualityService.evaluate_data_quality(session, project.id)
    await SnapshotService.capture_snapshot(session, project.id)

    logger.info(
        "Successfully seeded complete RiskZen Data Foundation",
        project_id=str(project.id),
        milestones=len(SEED_MILESTONES),
        work_items=len(SEED_WORK_ITEMS),
        team_members=len(TEAM_MEMBERS),
    )
    return project


async def main():
    """CLI runner for seed script."""
    async with async_session_factory() as session:
        await seed_database(session)


if __name__ == "__main__":
    asyncio.run(main())
