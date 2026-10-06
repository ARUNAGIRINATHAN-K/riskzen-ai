# RiskZen — Implementation Plan

**Document purpose:** Turn the strategic decisions in `IMPLEMENTATION-BLUEPRINT.md`, `MVP.md`, and `SPECIFICATION.md` into an assigned, dated, step-by-step operational roadmap.

**Owner:** Solo developer (all implementation tasks)
**Plan created:** 2026-09-30
**Plan start:** 2026-10-01
**Estimated MVP completion:** 2026-12-19
**Pilot window:** 2027-01-05 → 2027-02-27

---

## Timeline Overview

```text
Oct 01–07   Phase 0 — Project Setup & Validation          1 week
Oct 08–21   Phase 1 — Data Foundation                     2 weeks
Oct 22–Nov 04  Phase 2 — Risk Detection Engine            2 weeks
Nov 05–18   Phase 3 — Agentic Investigation Layer         2 weeks
Nov 19–Dec 05  Phase 4 — Frontend Dashboard               2.5 weeks
Dec 06–12   Phase 5 — Integration Testing & Evaluation    1 week
Dec 13–19   Phase 6 — Hardening & Documentation           1 week
Jan 05–Feb 27  Phase 7 — Pilot Deployment                 8 weeks
```

Total development: **~12 weeks** (Oct 01 – Dec 19)
Pilot: **8 weeks** (Jan 05 – Feb 27)

---

# Phase 0 — Project Setup & Validation

**Dates:** Oct 01 – Oct 07
**Goal:** Establish the development environment, repository structure, and validated risk taxonomy.
**Owner:** Developer

---

## Week 1: Oct 01 – Oct 07

### Day 1 — Oct 01 (Wed): Repository & Tooling

| # | Task | Status |
|---|---|---|
| 0.1 | Initialize monorepo structure (see directory layout below) | ☑ |
| 0.2 | Create `docker-compose.yml` with PostgreSQL + pgvector | ☑ |
| 0.3 | Scaffold FastAPI backend with project structure | ☑ |
| 0.4 | Scaffold Next.js frontend with TypeScript + Tailwind + shadcn/ui | ☑ |
| 0.5 | Verify Docker Compose starts all services cleanly | ☑ |
| 0.6 | Configure `.env.example` with all required environment variables | ☑ |

#### Target directory layout

```text
riskzen-ai/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── api/
│   │   ├── services/
│   │   ├── connectors/
│   │   ├── risk_engine/
│   │   ├── agent/
│   │   └── utils/
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   └── public/
└── docs/
    ├── IMPLEMENTATION-BLUEPRINT.md
    ├── MVP.md
    ├── SPECIFICATION.md
    └── IMPLEMENTATION-PLAN.md
```

---

### Day 2 — Oct 02 (Thu): Database Foundation

| # | Task | Status |
|---|---|---|
| 0.7 | Install and configure Alembic for migrations | ☑ |
| 0.8 | Enable `pgvector` extension in PostgreSQL | ☑ |
| 0.9 | Create initial migration: `projects` table | ☑ |
| 0.10 | Create health-check endpoint `GET /api/health` | ☑ |
| 0.11 | Verify backend connects to PostgreSQL through Docker Compose | ☑ |

---

### Day 3 — Oct 03 (Fri): Development Tooling

| # | Task | Status |
|---|---|---|
| 0.12 | Configure linting: `ruff` (backend), `eslint` + `prettier` (frontend) | ☑ |
| 0.13 | Configure `pytest` with test database fixture | ☑ |
| 0.14 | Set up structured logging with `structlog` | ☑ |
| 0.15 | Create `Makefile` or script commands: `dev`, `test`, `migrate`, `lint` | ☑ |
| 0.16 | Add `.gitignore` covering Python, Node, Docker, IDE files | ☑ |

---

### Days 4–5 — Oct 04–05 (Sat–Sun): Risk Taxonomy Research

| # | Task | Status |
|---|---|---|
| 0.17 | Research 5–10 recurring software-project risk patterns from PM literature | ☑ |
| 0.18 | For each pattern, identify observable leading indicators | ☑ |
| 0.19 | Map each indicator to a data source (GitHub issues, PRs, milestones, CSV) | ☑ |
| 0.20 | Document the validated risk taxonomy in `docs/risk-taxonomy.md` | ☑ |

---

### Days 6–7 — Oct 06–07 (Mon–Tue): Seed Data & Validation

| # | Task | Status |
|---|---|---|
| 0.21 | Design a realistic seed dataset simulating a 7-person software project | ☑ |
| 0.22 | Create seed script: projects, milestones, work items, dependencies | ☑ |
| 0.23 | Include deliberate risk patterns in seed data (blocked tasks, overdue deps) | ☑ |
| 0.24 | Verify seed data loads correctly and can be queried | ☑ |
| 0.25 | Write Phase 0 completion checklist and commit | ☑ |

---

### Phase 0 — Exit Criteria

- [x] Docker Compose brings up PostgreSQL + pgvector + FastAPI + Next.js
- [x] Health endpoint responds `200 OK`
- [x] At least 3 risk patterns have identified leading indicators mapped to data sources
- [x] Seed data loads and is queryable
- [x] Repository structure matches the target layout

---

# Phase 1 — Data Foundation

**Dates:** Oct 08 – Oct 21
**Goal:** Build the normalized data model, ingestion layer, GitHub connector, CSV importer, and data-quality checks.
**Owner:** Developer
**Depends on:** Phase 0 complete

---

## Week 2: Oct 08 – Oct 14

### Oct 08 (Wed): Core Data Model — Migrations

| # | Task | Status |
|---|---|---|
| 1.1 | Create SQLAlchemy models: `Project`, `Milestone`, `WorkItem` | ☑ |
| 1.2 | Create SQLAlchemy models: `Dependency`, `Team`, `TeamMember` | ☑ |
| 1.3 | Create SQLAlchemy models: `RiskEvent`, `Evidence` | ☑ |
| 1.4 | Create SQLAlchemy models: `Recommendation`, `Action`, `Outcome` | ☑ |
| 1.5 | Create SQLAlchemy model: `AuditLog` | ☑ |
| 1.6 | Generate and run Alembic migration for all tables | ☑ |

---

### Oct 09 (Thu): Pydantic Schemas & Base CRUD

| # | Task | Status |
|---|---|---|
| 1.7 | Create Pydantic request/response schemas for all entities | ☑ |
| 1.8 | Implement base CRUD service layer (create, read, update, list) | ☑ |
| 1.9 | Write unit tests for Project CRUD operations | ☑ |

---

### Oct 10 (Fri): Project Management API

| # | Task | Status |
|---|---|---|
| 1.10 | `POST /api/projects` — create project | ☑ |
| 1.11 | `GET /api/projects` — list projects | ☑ |
| 1.12 | `GET /api/projects/{id}` — project detail with summary stats | ☑ |
| 1.13 | `PATCH /api/projects/{id}` — update project status | ☑ |
| 1.14 | `GET /api/projects/{id}/summary` — work item / milestone / dependency counts | ☑ |
| 1.15 | Write API tests for project endpoints | ☑ |

---

### Oct 11–12 (Sat–Sun): Connector Abstraction

| # | Task | Status |
|---|---|---|
| 1.16 | Design `BaseConnector` abstract class with `connect()`, `sync()`, `status()` | ☑ |
| 1.17 | Define `ConnectorConfig` schema (type, credentials, sync interval) | ☑ |
| 1.18 | Create `DataSource` model (project_id, type, config, last_synced, status) | ☑ |
| 1.19 | `POST /api/projects/{id}/sources` — register a data source | ☑ |
| 1.20 | `GET /api/projects/{id}/sources` — list connected sources with status | ☑ |
| 1.21 | Write connector abstraction tests | ☑ |

---

### Oct 13 (Mon): GitHub Connector — Issues & Milestones

| # | Task | Status |
|---|---|---|
| 1.22 | Implement `GitHubConnector` extending `BaseConnector` | ☑ |
| 1.23 | Fetch GitHub Issues → normalize to `WorkItem` | ☑ |
| 1.24 | Fetch GitHub Milestones → normalize to `Milestone` | ☑ |
| 1.25 | Map GitHub labels/assignees to work item fields | ☑ |
| 1.26 | Handle pagination for large repositories | ☑ |
| 1.27 | Store `external_id` for deduplication on re-sync | ☑ |

---

### Oct 14 (Tue): GitHub Connector — PRs, Dependencies & Events

| # | Task | Status |
|---|---|---|
| 1.28 | Fetch Pull Requests → extract review status, merge time, CI status | ☑ |
| 1.29 | Extract cross-references between issues as `Dependency` records | ☑ |
| 1.30 | Parse "blocked by" / "depends on" keywords in issue bodies | ☑ |
| 1.31 | Implement incremental sync (only fetch since `last_synced`) | ☑ |
| 1.32 | Write integration tests with mocked GitHub API responses | ☑ |

---

## Week 3: Oct 15 – Oct 21

### Oct 15 (Wed): CSV Budget Importer

| # | Task | Status |
|---|---|---|
| 1.33 | Define expected CSV schema: `month`, `category`, `planned`, `actual` | ☑ |
| 1.34 | Implement `CSVBudgetConnector` extending `BaseConnector` | ☑ |
| 1.35 | `POST /api/projects/{id}/budget/upload` — accept CSV file | ☑ |
| 1.36 | Validate and normalize budget rows into `BudgetRecord` model | ☑ |
| 1.37 | Handle re-upload: replace previous budget data for same period | ☑ |
| 1.38 | Write tests with valid and malformed CSV files | ☑ |

---

### Oct 16 (Thu): Data Quality Engine

| # | Task | Status |
|---|---|---|
| 1.39 | Create `DataQualityCheck` model (project_id, check_type, result, details) | ☑ |
| 1.40 | Implement check: work items missing due dates | ☑ |
| 1.41 | Implement check: stale work items (no update > N days) | ☑ |
| 1.42 | Implement check: milestones missing target dates | ☑ |
| 1.43 | Implement check: dependencies with unresolved targets | ☑ |
| 1.44 | Implement check: budget data coverage / gaps | ☑ |
| 1.45 | Calculate overall data-quality score (0–100%) | ☑ |
| 1.46 | `GET /api/projects/{id}/data-quality` — return quality report | ☑ |

---

### Oct 17 (Fri): Historical Snapshots

| # | Task | Status |
|---|---|---|
| 1.47 | Create `ProjectSnapshot` model (project_id, snapshot_date, state_json) | ☑ |
| 1.48 | Implement snapshot service: capture current project state as JSON | ☑ |
| 1.49 | Schedule daily snapshot creation (store in DB, not filesystem) | ☑ |
| 1.50 | `GET /api/projects/{id}/snapshots` — list available snapshots | ☑ |
| 1.51 | Write snapshot creation and retrieval tests | ☑ |

---

### Oct 18–19 (Sat–Sun): Work Item & Milestone APIs

| # | Task | Status |
|---|---|---|
| 1.52 | `GET /api/projects/{id}/work-items` — list with filters (status, priority, assignee) | ☑ |
| 1.53 | `GET /api/projects/{id}/milestones` — list with completion stats | ☑ |
| 1.54 | `GET /api/projects/{id}/dependencies` — list with blocked/resolved status | ☑ |
| 1.55 | `GET /api/projects/{id}/timeline` — milestone timeline with work item mapping | ☑ |
| 1.56 | Write API tests for all listing endpoints | ☑ |

---

### Oct 20 (Mon): Sync Scheduler

| # | Task | Status |
|---|---|---|
| 1.57 | Integrate APScheduler or equivalent for periodic sync jobs | ☑ |
| 1.58 | Create `SyncJob` model (source_id, started_at, status, items_synced, errors) | ☑ |
| 1.59 | Implement configurable sync intervals per data source | ☑ |
| 1.60 | `POST /api/projects/{id}/sync` — trigger manual sync | ☑ |
| 1.61 | `GET /api/projects/{id}/sync-history` — list recent sync jobs | ☑ |

---

### Oct 21 (Tue): Phase 1 Integration & Verification

| # | Task | Status |
|---|---|---|
| 1.62 | End-to-end test: create project → connect GitHub → sync → verify data | ☑ |
| 1.63 | End-to-end test: upload CSV budget → verify budget records | ☑ |
| 1.64 | Verify data-quality score updates after sync | ☑ |
| 1.65 | Update seed script to use connector layer instead of direct inserts | ☑ |
| 1.66 | Commit, tag `v0.1.0-data-foundation` | ☑ |

---

### Phase 1 — Exit Criteria

- [x] All 10 core entities have working models, migrations, and CRUD
- [x] GitHub connector fetches issues, milestones, PRs, and dependencies
- [x] CSV budget import works with validation
- [x] Data-quality score is computed and served via API
- [x] Sync scheduler runs periodically and logs results
- [x] End-to-end data flow verified from source to database

---

# Phase 2 — Risk Detection Engine

**Dates:** Oct 22 – Nov 04
**Goal:** Implement deterministic risk signal detection across all 7 categories. This must work **without any LLM**.
**Owner:** Developer
**Depends on:** Phase 1 complete

---

## Week 4: Oct 22 – Oct 28

### Oct 22 (Wed): Risk Engine Architecture

| # | Task | Status |
|---|---|---|
| 2.1 | Design `RiskSignal` dataclass (category, signal_type, severity, value, threshold, metadata) | ☐ |
| 2.2 | Design `BaseRiskRule` abstract class with `evaluate(project_state) → list[RiskSignal]` | ☐ |
| 2.3 | Create `RiskEngineService` that orchestrates all rules | ☐ |
| 2.4 | Create `RiskThreshold` model (project_id, category, signal_type, warning, critical) | ☐ |
| 2.5 | `GET/PUT /api/projects/{id}/thresholds` — view/configure thresholds | ☐ |

---

### Oct 23 (Thu): Schedule Risk Rules

| # | Task | Status |
|---|---|---|
| 2.6 | Rule: overdue tasks (due_date < today, status != done) | ☐ |
| 2.7 | Rule: milestone slippage (items behind schedule vs target date) | ☐ |
| 2.8 | Rule: increasing cycle time (moving average over last N completed items) | ☐ |
| 2.9 | Rule: aging work (open items with no updates > N days) | ☐ |
| 2.10 | Rule: declining completion rate (completed items per week trending down) | ☐ |
| 2.11 | Write unit tests for each schedule rule with fixture data | ☐ |

---

### Oct 24 (Fri): Dependency Risk Rules

| # | Task | Status |
|---|---|---|
| 2.12 | Rule: blocked tasks exceeding threshold (blocked > N days) | ☐ |
| 2.13 | Rule: overdue upstream dependencies | ☐ |
| 2.14 | Rule: dependency concentration (single work item blocks > N items) | ☐ |
| 2.15 | Rule: cross-team handoff delays | ☐ |
| 2.16 | Write unit tests for dependency rules | ☐ |

---

### Oct 25–26 (Sat–Sun): Scope & Capacity Risk Rules

| # | Task | Status |
|---|---|---|
| 2.17 | Rule: scope growth (new work items created this cycle vs previous) | ☐ |
| 2.18 | Rule: requirement churn (items changing priority or description frequently) | ☐ |
| 2.19 | Rule: reopened work items count | ☐ |
| 2.20 | Rule: workload concentration (top assignee has > X% of open items) | ☐ |
| 2.21 | Rule: excessive WIP (open items per person > threshold) | ☐ |
| 2.22 | Rule: single-owner bottleneck (critical items owned by one person) | ☐ |
| 2.23 | Write unit tests for scope and capacity rules | ☐ |

---

### Oct 27 (Mon): Quality & Budget Risk Rules

| # | Task | Status |
|---|---|---|
| 2.24 | Rule: defect growth (bug-labeled items increasing over periods) | ☐ |
| 2.25 | Rule: reopened issues trend | ☐ |
| 2.26 | Rule: failed CI builds (from GitHub PR data) | ☐ |
| 2.27 | Rule: actual vs planned budget variance exceeding threshold | ☐ |
| 2.28 | Rule: burn-rate acceleration | ☐ |
| 2.29 | Write unit tests for quality and budget rules | ☐ |

---

### Oct 28 (Tue): Decision Latency Rules

| # | Task | Status |
|---|---|---|
| 2.30 | Rule: long-running blockers (items labeled "blocked" > N days) | ☐ |
| 2.31 | Rule: overdue approvals (PRs awaiting review > N days) | ☐ |
| 2.32 | Rule: unresolved decision items (issues labeled "decision-needed" aging) | ☐ |
| 2.33 | Write unit tests for decision latency rules | ☐ |

---

## Week 5: Oct 29 – Nov 04

### Oct 29 (Wed): Risk Scoring Engine

| # | Task | Status |
|---|---|---|
| 2.34 | Implement weighted risk propensity score per category | ☐ |
| 2.35 | Aggregate category scores into overall project risk level (Low/Medium/High/Critical) | ☐ |
| 2.36 | Make category weights configurable per project | ☐ |
| 2.37 | Calculate confidence based on data quality + signal strength | ☐ |
| 2.38 | Write scoring engine tests with known inputs and expected outputs | ☐ |

---

### Oct 30 (Thu): Risk Event Creation & Storage

| # | Task | Status |
|---|---|---|
| 2.39 | When engine detects a material risk: create `RiskEvent` record | ☐ |
| 2.40 | Attach contributing `RiskSignal` records as evidence | ☐ |
| 2.41 | Implement deduplication: don't create duplicate events for the same ongoing risk | ☐ |
| 2.42 | Implement risk status transitions: `new → active → mitigated → resolved → closed` | ☐ |
| 2.43 | Write risk event lifecycle tests | ☐ |

---

### Oct 31 (Fri): Risk History & Trends

| # | Task | Status |
|---|---|---|
| 2.44 | Create `RiskHistory` model (risk_id, timestamp, severity, score, status) | ☐ |
| 2.45 | Record severity changes over time for each risk event | ☐ |
| 2.46 | `GET /api/projects/{id}/risks` — list active risks sorted by severity | ☐ |
| 2.47 | `GET /api/projects/{id}/risks/{risk_id}` — detail with history | ☐ |
| 2.48 | `GET /api/projects/{id}/risk-summary` — category breakdown with trends | ☐ |

---

### Nov 01–02 (Sat–Sun): Scheduled Risk Evaluation

| # | Task | Status |
|---|---|---|
| 2.49 | Integrate risk engine with sync scheduler (run after each data sync) | ☐ |
| 2.50 | Add manual trigger: `POST /api/projects/{id}/evaluate` | ☐ |
| 2.51 | Create `RiskEvaluation` log (project_id, timestamp, signals_detected, events_created) | ☐ |
| 2.52 | Verify end-to-end: sync data → run engine → risk events appear | ☐ |

---

### Nov 03 (Mon): Threshold Configuration API

| # | Task | Status |
|---|---|---|
| 2.53 | Provide recommended default thresholds per risk category | ☐ |
| 2.54 | `PUT /api/projects/{id}/thresholds` — override defaults | ☐ |
| 2.55 | Validate threshold values (non-negative, sensible ranges) | ☐ |
| 2.56 | Apply configured thresholds in all risk rules | ☐ |

---

### Nov 04 (Tue): Phase 2 Verification

| # | Task | Status |
|---|---|---|
| 2.57 | End-to-end test: seed data with known risks → engine detects them correctly | ☐ |
| 2.58 | Verify no false positives in seed data scenarios | ☐ |
| 2.59 | Benchmark: engine evaluates 500+ work items in < 2 seconds | ☐ |
| 2.60 | Commit, tag `v0.2.0-risk-engine` | ☐ |

---

### Phase 2 — Exit Criteria

- [ ] All 7 risk categories have at least 2 working rules each
- [ ] Risk propensity scoring produces Low/Medium/High/Critical levels
- [ ] Risk events are created, deduplicated, and tracked with history
- [ ] Thresholds are configurable per project
- [ ] Engine runs automatically after data sync
- [ ] System detects known risks in seed data without any LLM involvement

---

# Phase 3 — Agentic Investigation Layer

**Dates:** Nov 05 – Nov 18
**Goal:** Add LangGraph workflow for AI-powered risk investigation, evidence retrieval, root-cause analysis, and recommendation generation.
**Owner:** Developer
**Depends on:** Phase 2 complete

---

## Week 6: Nov 05 – Nov 11

### Nov 05 (Wed): LLM Integration Setup

| # | Task | Status |
|---|---|---|
| 3.1 | Add Ollama service to `docker-compose.yml` | ☐ |
| 3.2 | Create `LLMService` abstraction with `generate()` and `embed()` methods | ☐ |
| 3.3 | Implement Ollama provider (local) | ☐ |
| 3.4 | Implement OpenAI-compatible provider (optional paid fallback) | ☐ |
| 3.5 | Add provider selection via environment variable | ☐ |
| 3.6 | Test basic completion and embedding generation | ☐ |

---

### Nov 06 (Thu): LangGraph Workflow Scaffold

| # | Task | Status |
|---|---|---|
| 3.7 | Install `langgraph` and configure in backend | ☐ |
| 3.8 | Define `InvestigationState` dataclass (risk_event, signals, evidence, analysis, recommendations) | ☐ |
| 3.9 | Create graph skeleton with nodes: `investigate → retrieve_evidence → analyze → recommend → review` | ☐ |
| 3.10 | Implement graph compilation and basic execution test | ☐ |

---

### Nov 07 (Fri): Investigator Node

| # | Task | Status |
|---|---|---|
| 3.11 | Build context assembly: gather risk signals, related work items, dependencies, milestone data | ☐ |
| 3.12 | Design investigation prompt template (structured, evidence-focused) | ☐ |
| 3.13 | Implement `investigate` node: LLM reasons over structured signals | ☐ |
| 3.14 | Parse and validate investigation output structure | ☐ |
| 3.15 | Test investigator with sample risk events | ☐ |

---

### Nov 08–09 (Sat–Sun): Evidence Retrieval Node

| # | Task | Status |
|---|---|---|
| 3.16 | Implement pgvector embedding storage for project documents | ☐ |
| 3.17 | Create embedding pipeline for work item descriptions, comments, PR descriptions | ☐ |
| 3.18 | Implement `retrieve_evidence` node: semantic search for relevant project records | ☐ |
| 3.19 | Also retrieve: related past risk events, dependency chains, milestone history | ☐ |
| 3.20 | Rank and filter evidence by relevance score | ☐ |
| 3.21 | Test evidence retrieval with known scenarios | ☐ |

---

### Nov 10 (Mon): Root-Cause Analysis Node

| # | Task | Status |
|---|---|---|
| 3.22 | Design root-cause analysis prompt (structured, must cite evidence) | ☐ |
| 3.23 | Implement `analyze` node: identify contributing factors from evidence | ☐ |
| 3.24 | Output: ranked list of contributing factors with supporting references | ☐ |
| 3.25 | Implement hallucination guard: cross-check claims against retrieved evidence | ☐ |
| 3.26 | Test with 3+ risk scenarios from seed data | ☐ |

---

### Nov 11 (Tue): Recommendation Generation Node

| # | Task | Status |
|---|---|---|
| 3.27 | Design recommendation prompt (practical, ownable, urgent, purposeful) | ☐ |
| 3.28 | Implement `recommend` node: produce 2–4 mitigation actions per risk | ☐ |
| 3.29 | Each recommendation includes: action, rationale, suggested owner, urgency | ☐ |
| 3.30 | Implement `review` node: quality check for unsupported claims / consistency | ☐ |
| 3.31 | Store recommendations in `Recommendation` table linked to risk event | ☐ |

---

## Week 7: Nov 12 – Nov 18

### Nov 12 (Wed): Human Approval API

| # | Task | Status |
|---|---|---|
| 3.32 | `GET /api/risks/{id}/recommendations` — list recommendations for a risk | ☐ |
| 3.33 | `POST /api/recommendations/{id}/approve` — approve recommendation | ☐ |
| 3.34 | `POST /api/recommendations/{id}/modify` — modify and approve | ☐ |
| 3.35 | `POST /api/recommendations/{id}/dismiss` — dismiss with reason | ☐ |
| 3.36 | `POST /api/recommendations/{id}/snooze` — snooze for N hours | ☐ |
| 3.37 | Record all decisions in `AuditLog` | ☐ |

---

### Nov 13 (Thu): Action Creation & Tracking API

| # | Task | Status |
|---|---|---|
| 3.38 | On approval: create `Action` record from recommendation | ☐ |
| 3.39 | `GET /api/projects/{id}/actions` — list actions (open, completed, overdue) | ☐ |
| 3.40 | `PATCH /api/actions/{id}` — update status, owner, due date | ☐ |
| 3.41 | `POST /api/actions/{id}/complete` — mark action complete | ☐ |
| 3.42 | Track overdue actions and surface in risk evaluation | ☐ |

---

### Nov 14 (Fri): Outcome Tracking & Feedback API

| # | Task | Status |
|---|---|---|
| 3.43 | `POST /api/risks/{id}/outcome` — record outcome (Yes/Partially/No/Not sure) | ☐ |
| 3.44 | Accept optional comment with outcome | ☐ |
| 3.45 | Link outcome to risk event, recommendations, and actions taken | ☐ |
| 3.46 | `POST /api/risks/{id}/feedback` — user rates alert (relevant, not relevant, incorrect, etc.) | ☐ |
| 3.47 | Store feedback for future model improvement | ☐ |

---

### Nov 15–16 (Sat–Sun): Agent Pipeline Integration

| # | Task | Status |
|---|---|---|
| 3.48 | Wire risk engine trigger → LangGraph pipeline for material risks | ☐ |
| 3.49 | Define "material risk" threshold that triggers agent investigation | ☐ |
| 3.50 | Implement async execution: agent investigation runs in background | ☐ |
| 3.51 | Store agent execution logs (input context, LLM calls, output) | ☐ |
| 3.52 | Add timeout and error handling for LLM calls | ☐ |

---

### Nov 17 (Mon): Agent Evaluation

| # | Task | Status |
|---|---|---|
| 3.53 | Create 5 test scenarios with expected investigation outcomes | ☐ |
| 3.54 | Run agent against each scenario, compare output quality | ☐ |
| 3.55 | Evaluate: factual grounding, evidence citations, recommendation practicality | ☐ |
| 3.56 | Tune prompts based on evaluation results | ☐ |

---

### Nov 18 (Tue): Phase 3 Verification

| # | Task | Status |
|---|---|---|
| 3.57 | End-to-end: data sync → risk detected → agent investigates → recommendations generated | ☐ |
| 3.58 | End-to-end: approve recommendation → action created → mark complete → outcome recorded | ☐ |
| 3.59 | Verify audit trail captures all decisions | ☐ |
| 3.60 | Commit, tag `v0.3.0-agent-layer` | ☐ |

---

### Phase 3 — Exit Criteria

- [ ] LangGraph workflow executes: investigate → evidence → analyze → recommend → review
- [ ] Agent produces structured risk alerts with evidence, contributing factors, and recommendations
- [ ] Recommendations can be approved, modified, dismissed, or snoozed via API
- [ ] Actions are created from approved recommendations and tracked to completion
- [ ] Outcome feedback is recorded
- [ ] Full audit trail is maintained
- [ ] Agent runs reliably with Ollama (local) or optional cloud LLM

---

# Phase 4 — Frontend Dashboard

**Dates:** Nov 19 – Dec 05
**Goal:** Build the complete user-facing dashboard with all MVP screens.
**Owner:** Developer
**Depends on:** Phase 3 API endpoints complete

---

## Week 8: Nov 19 – Nov 25

### Nov 19 (Wed): Design System & Layout

| # | Task | Status |
|---|---|---|
| 4.1 | Configure shadcn/ui component library | ☐ |
| 4.2 | Set up design tokens: color palette, typography (Inter/Outfit), spacing | ☐ |
| 4.3 | Build app shell: sidebar navigation, top bar, main content area | ☐ |
| 4.4 | Implement dark/light mode toggle | ☐ |
| 4.5 | Create reusable layout components: PageHeader, Card, StatusBadge | ☐ |
| 4.6 | Set up API client with `fetch` / `axios` and type-safe hooks | ☐ |

---

### Nov 20 (Thu): Project List & Onboarding

| # | Task | Status |
|---|---|---|
| 4.7 | Projects list page with health indicator per project | ☐ |
| 4.8 | "New Project" flow: name, type, description | ☐ |
| 4.9 | "Connect Source" flow: select GitHub / CSV, enter credentials | ☐ |
| 4.10 | Connection status display (connected, syncing, error) | ☐ |
| 4.11 | Initial data import progress indicator | ☐ |
| 4.12 | Data coverage summary after import (work items, milestones, deps, quality %) | ☐ |

---

### Nov 21 (Fri): Project Health Dashboard — Top Section

| # | Task | Status |
|---|---|---|
| 4.13 | Overall project health indicator (color-coded: green/yellow/orange/red) | ☐ |
| 4.14 | Risk distribution chart (by category: schedule, dependency, scope, etc.) | ☐ |
| 4.15 | Data quality score with breakdown | ☐ |
| 4.16 | Last synced timestamp | ☐ |
| 4.17 | Quick stats row: open risks, overdue actions, upcoming milestones | ☐ |

---

### Nov 22–23 (Sat–Sun): Dashboard — Risk & Milestone Sections

| # | Task | Status |
|---|---|---|
| 4.18 | "Top Emerging Risks" section — list of risk cards sorted by severity | ☐ |
| 4.19 | Risk card component: severity badge, title, affected milestone, primary evidence point, recommended action CTA | ☐ |
| 4.20 | "Milestone Forecast" section — timeline with health indicators | ☐ |
| 4.21 | "Dependency Bottlenecks" section — blocked items and their blockers | ☐ |
| 4.22 | "Overdue Actions" section — actions needing attention | ☐ |

---

### Nov 24 (Mon): Risk Detail Page

| # | Task | Status |
|---|---|---|
| 4.23 | Risk header: severity, category, confidence, status, detected date | ☐ |
| 4.24 | "Potential Impact" section with affected milestones and work items | ☐ |
| 4.25 | "Evidence" section — list of supporting signals with source references | ☐ |
| 4.26 | "Contributing Factors" section — ranked root-cause list | ☐ |
| 4.27 | "Risk Timeline" — severity changes over time (chart) | ☐ |
| 4.28 | "Agent Explanation" — AI-generated narrative explanation | ☐ |

---

### Nov 25 (Tue): Risk Detail — Recommendations & Actions

| # | Task | Status |
|---|---|---|
| 4.29 | "Recommended Actions" section with action cards | ☐ |
| 4.30 | Each card: action description, rationale, suggested owner, urgency | ☐ |
| 4.31 | Approval controls: Approve, Modify, Dismiss, Snooze buttons | ☐ |
| 4.32 | Modify modal: edit action description, change owner/due date | ☐ |
| 4.33 | Dismiss modal: require reason for dismissal | ☐ |
| 4.34 | "Action History" section — past actions taken for this risk | ☐ |

---

## Week 9: Nov 26 – Dec 02

### Nov 26 (Wed): Outcome & Feedback UI

| # | Task | Status |
|---|---|---|
| 4.35 | Outcome prompt at milestone completion (Yes/Partially/No/Not sure) | ☐ |
| 4.36 | Optional comment field with outcome | ☐ |
| 4.37 | Alert-level feedback buttons: Relevant, Not relevant, Already known, Incorrect | ☐ |
| 4.38 | Feedback confirmation toast notifications | ☐ |

---

### Nov 27 (Thu): Configuration & Threshold Settings

| # | Task | Status |
|---|---|---|
| 4.39 | Project settings page: monitoring categories toggles | ☐ |
| 4.40 | Threshold configuration form per risk category | ☐ |
| 4.41 | "Restore Defaults" option | ☐ |
| 4.42 | Connected sources management (view status, reconnect, remove) | ☐ |
| 4.43 | Manual sync trigger button | ☐ |

---

### Nov 28 (Fri): Risk List & Filters

| # | Task | Status |
|---|---|---|
| 4.44 | Full risk list page with filters: severity, category, status, date range | ☐ |
| 4.45 | Sort by: severity, detected date, last updated | ☐ |
| 4.46 | Bulk actions: dismiss selected, snooze selected | ☐ |
| 4.47 | Search within risk events | ☐ |

---

### Nov 29–30 (Sat–Sun): Actions List & Audit Trail

| # | Task | Status |
|---|---|---|
| 4.48 | Actions page: grouped by status (pending, in progress, completed, overdue) | ☐ |
| 4.49 | Action detail: source risk, recommendation, owner, due date, status | ☐ |
| 4.50 | Complete action button with optional outcome comment | ☐ |
| 4.51 | Audit trail page: chronological log of all risk events, decisions, actions | ☐ |
| 4.52 | Audit entry: timestamp, event type, details, user | ☐ |

---

### Dec 01 (Mon): Weekly Risk Summary View

| # | Task | Status |
|---|---|---|
| 4.53 | Weekly summary page: new risks, resolved risks, risk counts by severity | ☐ |
| 4.54 | Early warnings count | ☐ |
| 4.55 | Actions completed / overdue this week | ☐ |
| 4.56 | Comparison with previous week | ☐ |

---

### Dec 02 (Tue): Responsive Design & Polish

| # | Task | Status |
|---|---|---|
| 4.57 | Verify all pages render correctly on desktop (1440px, 1920px) | ☐ |
| 4.58 | Verify all pages render acceptably on tablet (768px) | ☐ |
| 4.59 | Add loading skeletons for all data-dependent components | ☐ |
| 4.60 | Add empty states for all list views | ☐ |
| 4.61 | Add error boundary and error display components | ☐ |
| 4.62 | Micro-animations: card hover effects, status transitions, chart animations | ☐ |

---

## Week 9.5: Dec 03 – Dec 05

### Dec 03 (Wed): Frontend–Backend Integration Testing

| # | Task | Status |
|---|---|---|
| 4.63 | Full user journey test: create project → connect GitHub → view dashboard | ☐ |
| 4.64 | Full user journey test: risk appears → view detail → approve recommendation → action created | ☐ |
| 4.65 | Full user journey test: complete action → record outcome → view audit trail | ☐ |
| 4.66 | Test budget CSV upload → budget risk signals appear | ☐ |

---

### Dec 04 (Thu): Accessibility & SEO

| # | Task | Status |
|---|---|---|
| 4.67 | Add proper `<title>` tags per page | ☐ |
| 4.68 | Add meta descriptions | ☐ |
| 4.69 | Verify heading hierarchy (single h1 per page) | ☐ |
| 4.70 | Keyboard navigation for all interactive elements | ☐ |
| 4.71 | ARIA labels for status indicators and charts | ☐ |

---

### Dec 05 (Fri): Phase 4 Verification

| # | Task | Status |
|---|---|---|
| 4.72 | Verify all dashboard sections display correctly with real data | ☐ |
| 4.73 | Screenshot all major views for documentation | ☐ |
| 4.74 | Commit, tag `v0.4.0-dashboard` | ☐ |

---

### Phase 4 — Exit Criteria

- [ ] Project onboarding flow works end-to-end
- [ ] Dashboard answers "what needs my attention today?" within seconds
- [ ] Risk cards display severity, evidence, and recommended action
- [ ] Risk detail page shows full investigation with evidence and root-cause analysis
- [ ] Approve/Modify/Dismiss/Snooze controls work and are audited
- [ ] Actions are trackable from creation to completion to outcome
- [ ] Feedback can be submitted on every alert
- [ ] Weekly summary view aggregates risk changes
- [ ] UI has dark mode, responsive layout, loading states, and empty states

---

# Phase 5 — Integration Testing & Evaluation

**Dates:** Dec 06 – Dec 12
**Goal:** Validate the complete system against historical scenarios and measure detection quality.
**Owner:** Developer
**Depends on:** Phase 4 complete

---

## Week 10: Dec 06 – Dec 12

### Dec 06 (Sat): Historical Replay Dataset

| # | Task | Status |
|---|---|---|
| 5.1 | Create 3 historical project scenarios with known risk outcomes | ☐ |
| 5.2 | Scenario A: schedule slippage due to blocked dependency (should detect) | ☐ |
| 5.3 | Scenario B: scope creep causing milestone risk (should detect) | ☐ |
| 5.4 | Scenario C: healthy project with minor issues (should NOT trigger critical alerts) | ☐ |
| 5.5 | Import all scenarios into the system | ☐ |

---

### Dec 07 (Sun): Detection Evaluation

| # | Task | Status |
|---|---|---|
| 5.6 | Run risk engine against all 3 scenarios | ☐ |
| 5.7 | Measure: true positives, false positives, false negatives | ☐ |
| 5.8 | Calculate precision and recall | ☐ |
| 5.9 | Measure detection lead time (how early before the "actual" impact date) | ☐ |
| 5.10 | Document results in `docs/evaluation-results.md` | ☐ |

---

### Dec 08 (Mon): AI Investigation Evaluation

| # | Task | Status |
|---|---|---|
| 5.11 | For each detected risk: evaluate agent explanation quality | ☐ |
| 5.12 | Check: are all cited evidence items real records? (no hallucination) | ☐ |
| 5.13 | Check: are contributing factors logically supported? | ☐ |
| 5.14 | Check: are recommendations practical and specific? | ☐ |
| 5.15 | Rate each investigation on 1–5 scale across 4 dimensions | ☐ |

---

### Dec 09 (Tue): Performance & Reliability Testing

| # | Task | Status |
|---|---|---|
| 5.16 | Load test: import project with 500+ work items, measure sync time | ☐ |
| 5.17 | Load test: risk engine evaluation time with 500+ items | ☐ |
| 5.18 | Test connector resilience: simulate GitHub API failures | ☐ |
| 5.19 | Test agent resilience: simulate LLM timeout / error | ☐ |
| 5.20 | Verify graceful degradation (system works without LLM, just no agent explanations) | ☐ |

---

### Dec 10 (Wed): Security Review

| # | Task | Status |
|---|---|---|
| 5.21 | Verify all credentials stored in environment variables, not code | ☐ |
| 5.22 | Verify GitHub tokens are encrypted at rest in database | ☐ |
| 5.23 | Verify API endpoints validate input (no SQL injection, no XSS) | ☐ |
| 5.24 | Verify Docker containers run as non-root | ☐ |
| 5.25 | Review data flow: confirm no employee-level data leaks into agent prompts | ☐ |

---

### Dec 11 (Thu): Bug Fixes & Tuning

| # | Task | Status |
|---|---|---|
| 5.26 | Fix all critical bugs found during evaluation | ☐ |
| 5.27 | Tune risk thresholds based on evaluation false positives | ☐ |
| 5.28 | Adjust agent prompts based on investigation quality scores | ☐ |
| 5.29 | Improve evidence retrieval relevance if needed | ☐ |

---

### Dec 12 (Fri): Phase 5 Verification

| # | Task | Status |
|---|---|---|
| 5.30 | Compile evaluation report with precision, recall, lead time metrics | ☐ |
| 5.31 | Document known limitations and failure modes | ☐ |
| 5.32 | Commit, tag `v0.5.0-evaluated` | ☐ |

---

### Phase 5 — Exit Criteria

- [ ] 3+ historical scenarios tested with documented results
- [ ] Precision ≥ 60% for critical-risk alerts (pre-pilot baseline)
- [ ] Agent explanations rated ≥ 3/5 on grounding and relevance
- [ ] System handles 500+ work items within acceptable response times
- [ ] Graceful degradation without LLM verified
- [ ] No critical security issues open

---

# Phase 6 — Hardening & Documentation

**Dates:** Dec 13 – Dec 19
**Goal:** Prepare the system for pilot deployment with documentation, deployment guide, and final polish.
**Owner:** Developer
**Depends on:** Phase 5 complete

---

## Week 11: Dec 13 – Dec 19

### Dec 13 (Sat): Deployment Documentation

| # | Task | Status |
|---|---|---|
| 6.1 | Write `README.md` with project description, features, architecture overview | ☐ |
| 6.2 | Write `docs/deployment-guide.md` — Docker Compose setup, env vars, first run | ☐ |
| 6.3 | Write `docs/github-connector-setup.md` — creating a token, permissions needed | ☐ |
| 6.4 | Write `docs/csv-budget-format.md` — expected CSV column format | ☐ |

---

### Dec 14 (Sun): API Documentation

| # | Task | Status |
|---|---|---|
| 6.5 | Verify FastAPI auto-generated OpenAPI docs are complete | ☐ |
| 6.6 | Add descriptions to all API endpoints and schemas | ☐ |
| 6.7 | Create Postman / Bruno collection for manual API testing | ☐ |

---

### Dec 15 (Mon): Error Handling & Edge Cases

| # | Task | Status |
|---|---|---|
| 6.8 | Add global error handler with structured error responses | ☐ |
| 6.9 | Handle: empty projects (no data synced yet) | ☐ |
| 6.10 | Handle: GitHub token expired / invalid | ☐ |
| 6.11 | Handle: Ollama not running / model not pulled | ☐ |
| 6.12 | Handle: database connection lost during sync | ☐ |

---

### Dec 16 (Tue): Observability Setup

| # | Task | Status |
|---|---|---|
| 6.13 | Verify structured logs capture: sync events, risk detections, agent runs, user actions | ☐ |
| 6.14 | Add request tracing middleware (correlation IDs) | ☐ |
| 6.15 | Create `GET /api/admin/logs` — recent agent execution logs | ☐ |
| 6.16 | Create `GET /api/admin/system-status` — services health check | ☐ |

---

### Dec 17 (Wed): Pilot Preparation

| # | Task | Status |
|---|---|---|
| 6.17 | Create pilot onboarding guide for participating PM | ☐ |
| 6.18 | Create feedback collection form template | ☐ |
| 6.19 | Prepare pilot evaluation spreadsheet with weekly tracking columns | ☐ |
| 6.20 | Test full deployment from clean machine (Docker Compose up) | ☐ |

---

### Dec 18 (Thu): Final Testing

| # | Task | Status |
|---|---|---|
| 6.21 | Run complete test suite (unit + integration + e2e) | ☐ |
| 6.22 | Fix any remaining test failures | ☐ |
| 6.23 | Verify all Docker images build successfully | ☐ |
| 6.24 | Test deployment on a separate machine / VM if available | ☐ |

---

### Dec 19 (Fri): MVP Release

| # | Task | Status |
|---|---|---|
| 6.25 | Final code review pass | ☐ |
| 6.26 | Update `CHANGELOG.md` | ☐ |
| 6.27 | Commit, tag `v1.0.0-mvp` | ☐ |
| 6.28 | Create GitHub release with description | ☐ |

---

### Phase 6 — Exit Criteria

- [ ] Full deployment documentation exists and is tested
- [ ] System starts cleanly from `docker compose up`
- [ ] All API endpoints are documented
- [ ] Error handling covers all critical edge cases
- [ ] Structured logs capture the complete decision chain
- [ ] Pilot materials are prepared
- [ ] `v1.0.0-mvp` is tagged and released

---

# Phase 7 — Pilot Deployment

**Dates:** Jan 05 – Feb 27, 2027
**Goal:** Deploy against 1–3 real projects, collect measurable evidence of value.
**Owner:** Developer + Pilot PM
**Depends on:** Phase 6 complete

---

## Pilot Schedule

| Week | Dates | Activity | Key Actions |
|---|---|---|---|
| **1** | Jan 05–09 | Baseline collection | Gather 4–8 weeks of historical risk data from the pilot project. Record: risk type, when it was first observable, when the team noticed, when it was escalated, impact, outcome. |
| **2** | Jan 12–16 | Data source integration | Connect the pilot project's GitHub repo + project tracker + CSV budget. Run initial sync. Review data quality score. Address any integration issues. |
| **3** | Jan 19–23 | Silent monitoring | System runs risk detection in the background. **No alerts shown to the PM yet.** Collect detected risks for internal review. |
| **4** | Jan 26–30 | Threshold tuning | Compare silently detected risks against PM's actual experience. Tune thresholds to reduce false positives. Adjust agent prompts if explanations are weak. |
| **5** | Feb 02–06 | Live alerts (week 1) | Expose alerts to the PM. Collect: accept/modify/dismiss decisions. Record first impressions. |
| **6** | Feb 09–13 | Live alerts (week 2) | Continue collecting decisions. Monitor: are recommendations being acted on? Weekly check-in with PM. |
| **7** | Feb 16–20 | Live alerts (week 3) | Focus on outcome tracking. Are earlier interventions happening? Collect feedback ratings. |
| **8** | Feb 23–27 | Evaluation | Compare AI-assisted process vs historical/manual process. Compile pilot report. |

---

## Pilot Metrics to Track Weekly

| Metric | How to Measure |
|---|---|
| Alerts generated | Count from database |
| Alerts accepted | Count approved / modified |
| Alerts dismissed | Count dismissed |
| Actions created | Count from actions table |
| Actions completed | Count completed actions |
| Actions overdue | Count overdue actions |
| Recommendation feedback | Relevant / Not relevant / Incorrect |
| Risk severity changes | Track HIGH → MEDIUM transitions |
| PM time spent | Self-reported by PM |
| Detection lead time | Compare "detected_at" vs "when PM would have found it manually" |

---

## Pilot Success Targets

| Measure | Target |
|---|---|
| Relevant alerts | ≥ 70% |
| Actionable recommendations | ≥ 60% |
| Critical-risk false positives | < 30% |
| Manager action rate | ≥ 60% |
| Investigation time reduction | ≥ 50% |
| User usefulness rating | ≥ 4/5 |

### Qualitative success

At least one PM statement equivalent to:

> "This surfaced something I would not have noticed early enough."

---

## Pilot Decision Rules

### → Scale

Proceed to broader deployment when:

- Alert relevance is consistently high
- Users regularly act on recommendations
- Detection occurs earlier than the existing review process
- System reliability is acceptable

### → Modify

Change the system when:

- Alerts are technically correct but operationally irrelevant
- Recommendations are too generic
- Data quality prevents reliable detection
- Users ignore alerts

### → Stop

Reconsider the approach if:

- False positives dominate after tuning
- Users consistently dismiss alerts
- Project outcomes show no measurable improvement
- Required data cannot be accessed reliably

---

# Task Summary by Phase

| Phase | Tasks | Duration | Cumulative |
|---|---|---|---|
| **0** — Setup & Validation | 25 tasks | 1 week | Week 1 |
| **1** — Data Foundation | 41 tasks | 2 weeks | Week 3 |
| **2** — Risk Detection Engine | 27 tasks | 2 weeks | Week 5 |
| **3** — Agentic Investigation | 28 tasks | 2 weeks | Week 7 |
| **4** — Frontend Dashboard | 42 tasks | 2.5 weeks | Week 9.5 |
| **5** — Testing & Evaluation | 16 tasks | 1 week | Week 10.5 |
| **6** — Hardening & Docs | 16 tasks | 1 week | Week 11.5 |
| **7** — Pilot | 8-week program | 8 weeks | Week 19.5 |
| **Total** | **195 dev tasks** | **~12 + 8 weeks** | |

---

# Functional Requirement Traceability

Every functional requirement from `SPECIFICATION.md` must be verifiable. This table maps requirements to the phase and tasks where they are implemented.

| Requirement | Description | Phase | Key Tasks |
|---|---|---|---|
| FR-01 | Project onboarding | Phase 1 | 1.10–1.21 |
| FR-02 | Data normalization | Phase 1 | 1.1–1.9, 1.22–1.35 |
| FR-03 | Data quality assessment | Phase 1 | 1.39–1.46 |
| FR-04 | Risk signal detection | Phase 2 | 2.1–2.33 |
| FR-05 | Risk scoring | Phase 2 | 2.34–2.38 |
| FR-06 | Agent investigation | Phase 3 | 3.7–3.31 |
| FR-07 | Evidence display | Phase 3 + 4 | 3.18–3.20, 4.25 |
| FR-08 | Recommendations | Phase 3 + 4 | 3.27–3.31, 4.29–4.34 |
| FR-09 | Human approval | Phase 3 + 4 | 3.32–3.37, 4.31–4.33 |
| FR-10 | Action tracking | Phase 3 + 4 | 3.38–3.42, 4.48–4.50 |
| FR-11 | Outcome tracking | Phase 3 + 4 | 3.43–3.47, 4.35–4.38 |
| FR-12 | Audit trail | Phase 3 + 4 | 3.37, 4.51–4.52 |

---

# Risk Mitigation During Implementation

| Risk | Likelihood | Mitigation in This Plan |
|---|---|---|
| Scope creep | High | Strict phase exit criteria; no feature additions until MVP tag |
| GitHub API rate limits | Medium | Incremental sync, caching, respect rate limit headers |
| Ollama model too slow | Medium | Task 3.4 provides cloud LLM fallback; agent is async |
| Agent hallucinations | Medium | Task 3.25 hallucination guard; task 5.12 evaluation check |
| Frontend complexity | Medium | shadcn/ui provides pre-built components; MVP-only features |
| Integration test gaps | Medium | End-to-end tests at every phase boundary |
| Pilot project unavailable | Medium | Seed data scenarios provide standalone evaluation capability |

---

# Key Dependencies

```text
Phase 0 ──→ Phase 1 ──→ Phase 2 ──→ Phase 3 ──→ Phase 4 ──→ Phase 5 ──→ Phase 6 ──→ Phase 7
  ↑                                      ↑            ↑
  Docker/DB ready                   LLM ready    API endpoints
                                   (Ollama)       ready for UI
```

- **Phase 1** cannot start until Docker + PostgreSQL are running (Phase 0)
- **Phase 3** requires Ollama model pulled and running
- **Phase 4** requires all API endpoints from Phases 1–3
- **Phase 5** requires both backend and frontend functional
- **Phase 7** requires a willing pilot PM with an active software project

---

# Version Tags

| Tag | Date | Milestone |
|---|---|---|
| `v0.1.0-data-foundation` | Oct 21 | Data model, connectors, quality checks |
| `v0.2.0-risk-engine` | Nov 04 | Deterministic risk detection (no LLM) |
| `v0.3.0-agent-layer` | Nov 18 | AI investigation, recommendations, approval |
| `v0.4.0-dashboard` | Dec 05 | Complete frontend |
| `v0.5.0-evaluated` | Dec 12 | Tested and tuned |
| `v1.0.0-mvp` | Dec 19 | Production-ready MVP |

---

# Weekly Checkpoint Template

Use this template every Friday to track progress:

```text
Week: ___
Phase: ___
Tasks completed: ___ / ___
Tasks blocked: ___
Blockers:
  1. ___
  2. ___
Key decisions made:
  1. ___
Risks identified:
  1. ___
Next week focus:
  1. ___
  2. ___
  3. ___
```
