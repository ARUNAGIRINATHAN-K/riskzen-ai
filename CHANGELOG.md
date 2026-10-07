# Changelog

All notable changes to RiskZen are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned

- LangGraph agent investigation workflow and root-cause analysis (Phase 3)
- Project health dashboard and interactive frontend UI (Phase 4)

---

## [0.2.0] — 2026-10-06 (Phase 2: Risk Detection Engine)

### Added

- **Deterministic Rule Base (7 Categories, 0% LLM)**:
  - **Schedule Risk**: `OverdueTasksRule`, `MilestoneSlippageRule`, `AgingWorkRule` (detecting deadline slips, overdue work items, and stalled execution).
  - **Dependency Risk**: `BlockedTasksRule`, `OverdueUpstreamDependenciesRule`, `DependencyConcentrationRule` (identifying upstream blockers, cascade delays, and high-impact nexus items).
  - **Scope Risk**: `ScopeGrowthRule`, `RequirementChurnRule` (detecting mid-milestone scope creep and unstable requirement churn).
  - **Capacity Risk**: `WorkloadConcentrationRule`, `ExcessiveWIPRule`, `SingleOwnerBottleneckRule` (identifying key-person bottlenecks and team overload).
  - **Quality Risk**: `DefectGrowthRule`, `CriticalDefectDebtRule`, `ReopenedIssuesRule` (detecting bug ratio spikes, SLA breaches, and regression rework).
  - **Budget Risk**: `BudgetVarianceRule`, `BurnRateAccelerationRule` (flagging cost variance and milestone burn rate pacing gaps).
  - **Decision Risk**: `LongRunningBlockersRule`, `StalledPRReviewsRule` (detecting prolonged blocker staleness and stalled code reviews).
- **Risk Scoring Engine (`scoring.py`)**:
  - Category propensity scoring and weighted aggregation into project risk levels (`Low`, `Medium`, `High`, `Critical`).
  - Signal depth and data quality confidence calculation.
- **Risk Event Deduplication & Audit Tracking**:
  - `RiskEvent` upsert with deterministic deduplication key `(project_id, category, signal_type, affected_milestone_id)`.
  - Comprehensive `RiskHistory` table tracking status transitions (`new -> active -> mitigated -> resolved -> closed -> dismissed`) and score progression.
- **Risk Engine Service (`RiskEngineService`)**:
  - Orchestrates in-memory `ProjectState` evaluation, signal extraction, scoring, deduplication, and persistence.
  - Automatic risk evaluation hook following data synchronization in `SyncService`.
- **Threshold Management API**:
  - `GET /api/v1/projects/{id}/thresholds` and `PUT /api/v1/projects/{id}/thresholds` with customizable thresholds per project.
- **Risk REST APIs**:
  - `POST /api/v1/projects/{id}/evaluate` (deterministic manual evaluation trigger).
  - `GET /api/v1/projects/{id}/risks` (filterable by category, severity, status).
  - `GET /api/v1/projects/{id}/risks/{risk_id}` (complete signal evidence and audit history).
  - `PATCH /api/v1/projects/{id}/risks/{risk_id}/status` (status updates with audit reason).
  - `GET /api/v1/projects/{id}/risk-summary` (aggregated category breakdown and health levels).
- **Automated Test Suite**:
  - Unit tests for all 7 risk categories rules in `test_risk_rules.py`.
  - Scoring engine tests in `test_risk_scoring.py`.
  - API endpoint tests in `test_risks_api.py`.
  - End-to-end benchmark & false-positive validation tests in `test_risk_engine_e2e.py` verifying sub-500ms execution on 500+ items.

---

## [0.1.0] — 2026-10-05 (Phase 1: Data Foundation)

### Added

- **Normalized Core Data Models**: Implemented SQLAlchemy 2.0 async models for all 10 core entities: `Project`, `DataSource`, `Milestone`, `WorkItem`, `Dependency`, `Team`, `TeamMember`, `RiskEvent`, `RiskSignal`, `Evidence`, `Recommendation`, `Action`, `Outcome`, `BudgetRecord`, `AuditLog`, `ProjectSnapshot`, `DataQualityCheck`, `RiskThreshold`, `SyncJob`, and `Embedding`.
- **Alembic Migration**: Created migration `002_core_data_foundation.py` creating all tables, foreign keys, indexes, and constraints.
- **Pydantic Schemas & Base CRUD**: Built comprehensive request/response schemas for work items, milestones, dependencies, teams, budgets, data quality checks, snapshots, and sync jobs.
- **Connector Abstraction & GitHub Connector**: Implemented `BaseConnector` abstraction and `GitHubConnector` fetching issues, milestones, and pull requests with pagination, normalization, and automatic dependency extraction from body keywords (`blocked by #ID`, `depends on #ID`).
- **CSV Financial Budget Importer**: Implemented `CSVBudgetConnector` and `BudgetService` with schema normalization, variance calculation (`actual - planned`), period replacement on re-upload, and budget summary reports.
- **Data Quality Engine**: Implemented `DataQualityService` evaluating 5 rule checks (missing due dates, stale items, missing target dates, unresolved dependencies, budget coverage) and computing a composite health reliability score (0–100%).
- **Historical Project Snapshots**: Implemented `SnapshotService` serializing point-in-time project states and metrics for trend analysis and historical replay.
- **Sync Scheduler & Sync History**: Integrated APScheduler in `app/scheduler/jobs.py` for periodic data sync and daily snapshot generation, with manual sync trigger (`POST /api/v1/projects/{id}/sync`) and sync execution audit history.
- **REST API Endpoints**: Created 18+ endpoints covering Projects, Work Items, Milestones, Timeline, Dependencies, Budget Upload, Data Quality, Snapshots, and Sync.
- **Automated Test Suite**: Added comprehensive test suite with 100% pass rate covering GitHub connector, CSV budget importer, data quality rules, work item/milestone flows, sync service, and REST API endpoints.

## [0.0.2] — 2026-10-04 (Phase 0: Project Setup & Validation)

### Added

- **Backend Architecture & Tooling**: Configured FastAPI monorepo structure, `pyproject.toml` with Ruff, Pytest, and async test fixtures (`conftest.py`).
- **Database & Migrations**: Configured Alembic with async SQLAlchemy support and initial migration `001_initial_schema.py` enabling the `pgvector` extension and establishing the `projects` and `data_sources` tables.
- **Observability & Health Checks**: Integrated `structlog` structured logging with console and JSON formatters. Enhanced `GET /health` and `GET /api/v1/health` endpoints with dynamic PostgreSQL connection checks and pgvector availability status.
- **Frontend Scaffolding**: Established Next.js TypeScript App Router layout with utility modules (`api-client.ts`, `utils.ts`) and TypeScript domain types (`project.ts`, `risk.ts`, `common.ts`).
- **Risk Taxonomy Research**: Published `docs/risk-taxonomy.md` defining 8 validated software project risk categories, observable leading indicators, PM literature citations, telemetry mappings, and severity triggers.
- **Realistic Seed Dataset**: Implemented `app/seed.py` simulating a 7-person team ("NovaPay Mobile Checkout") with deliberate risk patterns (milestone slip, cascading dependency blocks, developer bottleneck, stalled PRs, scope creep).

---

## [0.0.1] — 2026-09-30

### Added

- **IMPLEMENTATION-BLUEPRINT.md** — Strategic blueprint covering problem analysis, solution options, weighted decision matrix, architecture, agent design, implementation phases, risk register, ethics, sustainability, pilot design, and evaluation framework.
- **MVP.md** — Detailed MVP specification with concrete user journey (persona: Anita, PM), 11-step walkthrough from project connection through outcome tracking, user experience requirements, acceptance criteria, technology architecture, implementation plan, cost estimates, pilot design, and success criteria.
- **SPECIFICATION.md** — Functional specification with product definition, design principles, 12 functional requirements (FR-01 through FR-12), risk detection model across 7 categories, agent workflow, MVP data model (10 entities), UI requirements, non-functional requirements, success metrics, evaluation framework, pilot decision rules, and maturity roadmap (Levels 1–8).
- **PRD.md** — Product Requirements Document defining exactly what is being built and why. Contains 14 MVP features (F-01 through F-14), 19 user stories (US-01 through US-19), 15-step acceptance criteria, explicit exclusion list (17 items), non-functional requirements, quantitative success targets, data source scope, and glossary. Acts as the authoritative scope anchor.
- **ARCHITECTURE.md** — Technical architecture document covering system overview, technology stack with rationale, full project directory structure, backend 3-layer architecture, 33 REST API endpoints, database schema (14 tables with columns), connector pattern, risk engine design with scoring model, LangGraph agent workflow (5 nodes), frontend page structure, data flow diagrams, Docker Compose infrastructure, security architecture, observability strategy, scalability path, and 10 Architecture Decision Records.
- **IMPLEMENTATION-PLAN.md** — Operational roadmap with 195 individually trackable tasks across 7 phases, dated to the day (Oct 01 – Dec 19 development, Jan 05 – Feb 27 pilot), exit criteria per phase, functional requirement traceability matrix, version tags, dependency graph, risk mitigation table, and weekly checkpoint template.
- **CHANGELOG.md** — This file.
- **LICENSE** — Project license.
- **README.md** — Initial project readme.

---

<!-- Future version entries will follow this structure: -->

<!-- ## [1.0.0] — YYYY-MM-DD -->
<!-- ### Added -->
<!-- ### Changed -->
<!-- ### Fixed -->
<!-- ### Security -->

<!--
Version Roadmap (from IMPLEMENTATION-PLAN.md):

  [0.1.0]  Data Foundation        — Core data model, GitHub connector, CSV importer, data quality
  [0.2.0]  Risk Engine            — Deterministic risk detection across 7 categories (no LLM)
  [0.3.0]  Agent Layer            — LangGraph investigation, recommendations, human approval
  [0.4.0]  Dashboard              — Complete frontend with all MVP screens
  [0.5.0]  Evaluated              — Historical replay, precision/recall measurement, tuning
  [1.0.0]  MVP Release            — Production-ready MVP
-->

[Unreleased]: https://github.com/ARUNAGIRINATHAN-K/riskzen-ai/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/ARUNAGIRINATHAN-K/riskzen-ai/releases/tag/v0.0.1
