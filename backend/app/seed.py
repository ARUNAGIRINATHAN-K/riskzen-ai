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

from app.database import async_session_factory, engine
from app.models.project import DataSource, Project
from app.utils.logging import get_logger

logger = get_logger("riskzen.seed")

# Team Roster
TEAM_MEMBERS = [
    {"name": "Alex Chen", "role": "Tech Lead / Backend Senior", "email": "alex.chen@novapay.io"},
    {"name": "Priya Sharma", "role": "Senior Frontend Engineer", "email": "priya.sharma@novapay.io"},
    {"name": "Marcus Vance", "role": "Backend Engineer", "email": "marcus.vance@novapay.io"},
    {"name": "Elena Rostova", "role": "Mobile Engineer", "email": "elena.rostova@novapay.io"},
    {"name": "Dev Patel", "role": "Frontend / UI Engineer", "email": "dev.patel@novapay.io"},
    {"name": "Sara Lindqvist", "role": "QA / Test Automation Lead", "email": "sara.l@novapay.io"},
    {"name": "Carlos Mendez", "role": "DevOps Engineer", "email": "carlos.m@novapay.io"},
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
        "milestone": "Core Payment Engine & Tokenization",
        "labels": ["backend", "stripe", "payments"],
    },
    {
        "external_id": "NOVA-102",
        "title": "PCI-DSS Vault DB Migration Script & Key Rotation",
        "item_type": "task",
        "status": "in_progress",
        "priority": "critical",
        "assignee": "Marcus Vance",
        "milestone": "Core Payment Engine & Tokenization",
        "labels": ["database", "security", "pci-dss", "blocker"],
    },
    {
        "external_id": "NOVA-103",
        "title": "Tokenized Card Vault Retrieval Micro-Endpoint",
        "item_type": "task",
        "status": "open",
        "priority": "critical",
        "assignee": "Alex Chen",
        "milestone": "Core Payment Engine & Tokenization",
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
        "milestone": "Checkout UI & Digital Wallets",
        "labels": ["frontend", "mobile", "apple-pay"],
    },
    {
        "external_id": "NOVA-105",
        "title": "Apple Pay Session Validation & Crypto Signature Verification",
        "item_type": "feature",
        "status": "open",
        "priority": "critical",
        "assignee": "Alex Chen",
        "milestone": "Checkout UI & Digital Wallets",
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
        "milestone": "Checkout UI & Digital Wallets",
        "labels": ["frontend", "google-pay"],
    },
    {
        "external_id": "NOVA-107",
        "title": "Reopened: Shopping Cart Summary Desync on Network Retry",
        "item_type": "bug",
        "status": "open",
        "priority": "high",
        "assignee": "Priya Sharma",
        "milestone": "Checkout UI & Digital Wallets",
        "labels": ["bug", "reopened", "cart"],
    },
    {
        "external_id": "NOVA-108",
        "title": "PR #88: Core Payment State Machine Refactoring",
        "item_type": "decision",
        "status": "open",
        "priority": "high",
        "assignee": "Marcus Vance",
        "milestone": "Core Payment Engine & Tokenization",
        "labels": ["pr-review", "decision-latency", "stalled"],
    },
    {
        "external_id": "NOVA-109",
        "title": "Unestimated: Loyalty Points Redemption Widget at Checkout",
        "item_type": "feature",
        "status": "open",
        "priority": "medium",
        "assignee": None,
        "milestone": "Checkout UI & Digital Wallets",
        "labels": ["scope-creep", "unestimated", "growth-experiment"],
    },
    {
        "external_id": "NOVA-110",
        "title": "Unestimated: Multi-Currency Dynamic FX Rate Preview",
        "item_type": "feature",
        "status": "open",
        "priority": "medium",
        "assignee": None,
        "milestone": "Checkout UI & Digital Wallets",
        "labels": ["scope-creep", "unestimated", "fintech"],
    },
]


async def seed_database(session: AsyncSession) -> Project:
    """Seed project, data sources, and simulated telemetry."""
    # 1. Check if seed project already exists
    stmt = select(Project).where(Project.name == "NovaPay — Mobile Checkout Revamp")
    result = await session.execute(stmt)
    existing_project = result.scalar_one_or_none()

    if existing_project:
        logger.info("Seed project already exists", project_id=str(existing_project.id))
        return existing_project

    # 2. Create Project
    now = datetime.now(timezone.utc)
    project = Project(
        name="NovaPay — Mobile Checkout Revamp",
        description=(
            "Next-generation mobile checkout experience with 1-click biometric auth, "
            "Apple Pay, Google Pay, and localized zero-trust token storage."
        ),
        project_type="software",
        status="active",
        health="yellow",  # Yellow because of capacity concentration and blocked critical path
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
    await session.commit()
    await session.refresh(project)

    logger.info(
        "Successfully seeded RiskZen with NovaPay project",
        project_id=str(project.id),
        data_sources=len(project.data_sources),
        team_size=len(TEAM_MEMBERS),
        work_items=len(SEED_WORK_ITEMS),
    )
    return project


async def main():
    """CLI runner for seed script."""
    async with async_session_factory() as session:
        await seed_database(session)


if __name__ == "__main__":
    asyncio.run(main())
