# Architecture Document

**Product:** RiskZen
**Document type:** Technical Architecture
**Purpose:** Define how the application is structured, how components communicate, and why each technical decision was made. This is the authoritative reference for all implementation.
**Date:** 2026-09-30
**Status:** Active

---

# 1. Architecture Overview

## System Summary

RiskZen is a three-tier web application with an embedded AI agent layer:

```
┌─────────────────────────────────────────────────┐
│                   FRONTEND                      │
│              Next.js + TypeScript               │
│            Tailwind CSS + shadcn/ui             │
└────────────────────┬────────────────────────────┘
                     │ HTTP / REST
┌────────────────────┴────────────────────────────┐
│                   BACKEND                       │
│              Python + FastAPI                   │
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │
│  │ API      │  │ Risk      │  │ Agent        │  │
│  │ Layer    │  │ Engine    │  │ Orchestrator │  │
│  └──────────┘  └───────────┘  └──────────────┘  │
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐  │
│  │Connectors│  │ Scheduler │  │ LLM Service  │  │
│  └──────────┘  └───────────┘  └──────────────┘  │
└────────────────────┬────────────────────────────┘
                     │ SQL / pgvector
┌────────────────────┴────────────────────────────┐
│                  DATABASE                       │
│           PostgreSQL + pgvector                 │
└─────────────────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      ↓              ↓              ↓
   GitHub         CSV Files       Ollama
   (REST API)     (Upload)        (Local LLM)
```

## Architecture Style

**Modular monolith.** All backend logic runs in a single FastAPI process with clearly separated internal modules. This is deliberately not a microservices architecture — a monolith is simpler to develop, deploy, debug, and operate for a solo developer building an MVP.

The internal modules are designed with clean boundaries so they can be extracted into services later if needed.

---

# 2. Technology Decisions

| Layer | Choice | Rationale |
|---|---|---|
| **Frontend framework** | Next.js (App Router) | Server-side rendering, file-based routing, strong TypeScript support, large ecosystem |
| **Frontend language** | TypeScript | Type safety, better IDE support, fewer runtime errors |
| **CSS** | Tailwind CSS | Utility-first, rapid UI development, consistent design tokens |
| **Component library** | shadcn/ui | Pre-built accessible components, fully customizable, no vendor lock-in |
| **Backend framework** | FastAPI (Python) | Async support, automatic OpenAPI docs, Pydantic validation, strong ML/AI ecosystem |
| **Backend language** | Python 3.11+ | Best ecosystem for AI/ML, LangGraph, data processing |
| **ORM** | SQLAlchemy 2.0 | Mature, type-safe with mapped columns, async support |
| **Migrations** | Alembic | Standard for SQLAlchemy, supports auto-generation |
| **Database** | PostgreSQL 16 | Robust, open-source, supports pgvector, JSON columns, full-text search |
| **Vector storage** | pgvector | Avoids a separate vector DB; vectors live alongside relational data |
| **Agent framework** | LangGraph | Stateful workflows, checkpointing, human-in-the-loop interruption, retry support |
| **Local LLM** | Ollama | Free local inference, OpenAI-compatible API, no API key needed locally |
| **Task scheduling** | APScheduler | Lightweight, in-process, supports cron and interval schedules |
| **Logging** | structlog | Structured JSON logging, context binding, processor pipeline |
| **Containerization** | Docker + Docker Compose | Reproducible environments, single-command deployment |
| **Testing** | pytest (backend), Vitest (frontend) | Standard tools for each ecosystem |

### Decisions explicitly rejected

| Rejected Option | Reason |
|---|---|
| Separate vector database (Pinecone, Weaviate) | Unnecessary complexity; pgvector is sufficient for MVP scale |
| Microservices | Too much operational overhead for solo developer |
| Kubernetes | Docker Compose is sufficient for MVP deployment |
| Django | FastAPI is better suited for API-first + async + AI workloads |
| MongoDB | Relational data model with dependencies and references is better served by PostgreSQL |
| Redis (as primary cache) | PostgreSQL query performance is sufficient at MVP scale; add if needed |
| Celery | APScheduler is simpler for periodic jobs; add Celery only if task queues are needed |

---

# 3. Project Structure

```
riskzen-ai/
│
├── docker-compose.yml              # All services: db, backend, frontend, ollama
├── .env.example                    # Template for environment variables
├── Makefile                        # Dev commands: dev, test, migrate, lint, seed
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml              # Dependencies (uv/pip)
│   ├── alembic.ini
│   ├── alembic/
│   │   └── versions/              # Migration files
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI app creation, middleware, router mounting
│   │   ├── config.py              # Settings from environment variables
│   │   ├── database.py            # SQLAlchemy engine, session factory
│   │   │
│   │   ├── models/                # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── project.py         # Project, DataSource
│   │   │   ├── work_item.py       # WorkItem, Milestone, Dependency
│   │   │   ├── team.py            # Team, TeamMember
│   │   │   ├── risk.py            # RiskEvent, RiskSignal, RiskHistory
│   │   │   ├── evidence.py        # Evidence
│   │   │   ├── recommendation.py  # Recommendation, Action
│   │   │   ├── outcome.py         # Outcome, Feedback
│   │   │   ├── budget.py          # BudgetRecord
│   │   │   ├── audit.py           # AuditLog
│   │   │   └── snapshot.py        # ProjectSnapshot
│   │   │
│   │   ├── schemas/               # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── project.py
│   │   │   ├── work_item.py
│   │   │   ├── risk.py
│   │   │   ├── recommendation.py
│   │   │   ├── action.py
│   │   │   ├── outcome.py
│   │   │   └── common.py          # Shared schemas (pagination, errors)
│   │   │
│   │   ├── api/                   # FastAPI route handlers
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # Main router aggregating all sub-routers
│   │   │   ├── projects.py        # /api/projects
│   │   │   ├── work_items.py      # /api/projects/{id}/work-items
│   │   │   ├── milestones.py      # /api/projects/{id}/milestones
│   │   │   ├── dependencies.py    # /api/projects/{id}/dependencies
│   │   │   ├── risks.py           # /api/projects/{id}/risks, /api/risks/{id}
│   │   │   ├── recommendations.py # /api/recommendations/{id}
│   │   │   ├── actions.py         # /api/actions/{id}
│   │   │   ├── outcomes.py        # /api/risks/{id}/outcome
│   │   │   ├── data_quality.py    # /api/projects/{id}/data-quality
│   │   │   ├── sync.py            # /api/projects/{id}/sync
│   │   │   ├── thresholds.py      # /api/projects/{id}/thresholds
│   │   │   ├── budget.py          # /api/projects/{id}/budget
│   │   │   ├── audit.py           # /api/projects/{id}/audit
│   │   │   └── admin.py           # /api/admin (system status, logs)
│   │   │
│   │   ├── services/              # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── project_service.py
│   │   │   ├── sync_service.py
│   │   │   ├── data_quality_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── recommendation_service.py
│   │   │   ├── action_service.py
│   │   │   ├── outcome_service.py
│   │   │   ├── snapshot_service.py
│   │   │   └── audit_service.py
│   │   │
│   │   ├── connectors/            # External data source integrations
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # BaseConnector abstract class
│   │   │   ├── github.py          # GitHubConnector
│   │   │   └── csv_budget.py      # CSVBudgetConnector
│   │   │
│   │   ├── risk_engine/           # Deterministic risk detection
│   │   │   ├── __init__.py
│   │   │   ├── engine.py          # RiskEngineService orchestrator
│   │   │   ├── base_rule.py       # BaseRiskRule abstract class
│   │   │   ├── scoring.py         # Risk propensity scoring
│   │   │   ├── rules/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schedule.py    # OverdueTasksRule, MilestoneSlippageRule, etc.
│   │   │   │   ├── dependency.py  # BlockedTasksRule, UpstreamDelayRule, etc.
│   │   │   │   ├── scope.py       # ScopeGrowthRule, RequirementChurnRule, etc.
│   │   │   │   ├── capacity.py    # WorkloadConcentrationRule, ExcessiveWIPRule, etc.
│   │   │   │   ├── quality.py     # DefectGrowthRule, ReopenedIssuesRule, etc.
│   │   │   │   ├── budget.py      # BudgetVarianceRule, BurnRateRule, etc.
│   │   │   │   └── decision.py    # OverdueApprovalsRule, LongBlockersRule, etc.
│   │   │   └── thresholds.py      # Default thresholds and configuration
│   │   │
│   │   ├── agent/                 # AI investigation layer
│   │   │   ├── __init__.py
│   │   │   ├── graph.py           # LangGraph workflow definition
│   │   │   ├── state.py           # InvestigationState dataclass
│   │   │   ├── nodes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── investigate.py     # Context assembly + initial reasoning
│   │   │   │   ├── retrieve_evidence.py # pgvector similarity search + DB queries
│   │   │   │   ├── analyze.py         # Root-cause analysis
│   │   │   │   ├── recommend.py       # Mitigation recommendations
│   │   │   │   └── review.py          # Quality check / hallucination guard
│   │   │   ├── prompts/
│   │   │   │   ├── investigate.md
│   │   │   │   ├── analyze.md
│   │   │   │   ├── recommend.md
│   │   │   │   └── review.md
│   │   │   └── llm_service.py     # LLM abstraction (Ollama / OpenAI-compatible)
│   │   │
│   │   ├── scheduler/             # Periodic job scheduling
│   │   │   ├── __init__.py
│   │   │   └── jobs.py            # Sync jobs, risk evaluation jobs, snapshot jobs
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py         # structlog configuration
│   │       ├── errors.py          # Custom exception classes
│   │       └── pagination.py      # Pagination helpers
│   │
│   └── tests/
│       ├── conftest.py            # Test database fixture, test client
│       ├── test_api/
│       ├── test_services/
│       ├── test_connectors/
│       ├── test_risk_engine/
│       └── test_agent/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   │
│   ├── src/
│   │   ├── app/                   # Next.js App Router pages
│   │   │   ├── layout.tsx         # Root layout with sidebar, theme provider
│   │   │   ├── page.tsx           # Redirect to /projects
│   │   │   ├── projects/
│   │   │   │   ├── page.tsx                       # Project list
│   │   │   │   ├── new/page.tsx                   # New project wizard
│   │   │   │   └── [projectId]/
│   │   │   │       ├── page.tsx                   # Project dashboard
│   │   │   │       ├── risks/
│   │   │   │       │   ├── page.tsx               # Risk list with filters
│   │   │   │       │   └── [riskId]/page.tsx      # Risk detail page
│   │   │   │       ├── actions/page.tsx           # Action tracking
│   │   │   │       ├── summary/page.tsx           # Weekly summary
│   │   │   │       ├── audit/page.tsx             # Audit trail
│   │   │   │       └── settings/page.tsx          # Thresholds, sources
│   │   │   └── globals.css
│   │   │
│   │   ├── components/
│   │   │   ├── ui/                # shadcn/ui components (auto-generated)
│   │   │   ├── layout/
│   │   │   │   ├── sidebar.tsx
│   │   │   │   ├── top-bar.tsx
│   │   │   │   └── page-header.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── health-indicator.tsx
│   │   │   │   ├── risk-distribution-chart.tsx
│   │   │   │   ├── milestone-timeline.tsx
│   │   │   │   ├── dependency-bottlenecks.tsx
│   │   │   │   └── overdue-actions.tsx
│   │   │   ├── risks/
│   │   │   │   ├── risk-card.tsx
│   │   │   │   ├── risk-detail.tsx
│   │   │   │   ├── evidence-list.tsx
│   │   │   │   ├── contributing-factors.tsx
│   │   │   │   ├── risk-timeline-chart.tsx
│   │   │   │   └── approval-controls.tsx
│   │   │   ├── recommendations/
│   │   │   │   ├── recommendation-card.tsx
│   │   │   │   ├── modify-modal.tsx
│   │   │   │   └── dismiss-modal.tsx
│   │   │   ├── actions/
│   │   │   │   ├── action-card.tsx
│   │   │   │   └── action-list.tsx
│   │   │   ├── feedback/
│   │   │   │   ├── outcome-prompt.tsx
│   │   │   │   └── alert-feedback.tsx
│   │   │   ├── onboarding/
│   │   │   │   ├── connect-github.tsx
│   │   │   │   ├── upload-csv.tsx
│   │   │   │   └── data-coverage.tsx
│   │   │   └── common/
│   │   │       ├── status-badge.tsx
│   │   │       ├── severity-badge.tsx
│   │   │       ├── loading-skeleton.tsx
│   │   │       ├── empty-state.tsx
│   │   │       └── error-boundary.tsx
│   │   │
│   │   ├── lib/
│   │   │   ├── api-client.ts      # Typed fetch wrapper for backend API
│   │   │   ├── hooks/             # Custom React hooks for data fetching
│   │   │   │   ├── use-project.ts
│   │   │   │   ├── use-risks.ts
│   │   │   │   ├── use-actions.ts
│   │   │   │   └── use-dashboard.ts
│   │   │   └── utils.ts           # Formatting, date helpers
│   │   │
│   │   └── types/
│   │       ├── project.ts
│   │       ├── risk.ts
│   │       ├── recommendation.ts
│   │       ├── action.ts
│   │       └── common.ts
│   │
│   └── public/
│       └── favicon.ico
│
└── docs/
    ├── IMPLEMENTATION-BLUEPRINT.md
    ├── MVP.md
    ├── SPECIFICATION.md
    ├── PRD.md
    ├── IMPLEMENTATION-PLAN.md
    ├── ARCHITECTURE.md
    ├── risk-taxonomy.md
    └── evaluation-results.md
```

---

# 4. Backend Architecture

## Layer Separation

The backend follows a strict three-layer architecture. Each layer has a clear responsibility and may only call the layer directly below it.

```
┌─────────────────────────────────┐
│         API Layer               │  Handles HTTP requests/responses,
│   (FastAPI route handlers)      │  input validation, serialization.
│                                 │  Contains no business logic.
└────────────────┬────────────────┘
                 │ calls
┌────────────────┴────────────────┐
│       Service Layer             │  Contains all business logic.
│   (service classes/functions)   │  Orchestrates data access,
│                                 │  risk engine, and agent calls.
└────────────────┬────────────────┘
                 │ calls
┌────────────────┴────────────────┐
│        Data Layer               │  SQLAlchemy models, database
│   (models, repositories)        │  queries, connector I/O.
│                                 │  No business logic.
└─────────────────────────────────┘
```

### Rules

- **API layer** never queries the database directly. It calls service functions.
- **Service layer** never returns SQLAlchemy model objects to the API layer. It returns Pydantic schemas.
- **Data layer** never raises HTTP exceptions. It raises domain exceptions that the service or API layer translates.
- **Connectors** are called by the service layer, never by the API layer directly.
- **Risk engine** is called by the service layer after data sync completes.
- **Agent** is called by the service layer when a material risk is detected.

---

## API Design

### Base URL

```
/api/v1
```

### Resource Routes

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/projects` | Create project |
| `GET` | `/projects` | List projects |
| `GET` | `/projects/{id}` | Project detail |
| `PATCH` | `/projects/{id}` | Update project |
| `POST` | `/projects/{id}/sources` | Register data source |
| `GET` | `/projects/{id}/sources` | List data sources |
| `POST` | `/projects/{id}/sync` | Trigger manual sync |
| `GET` | `/projects/{id}/sync-history` | Sync job history |
| `POST` | `/projects/{id}/budget/upload` | Upload CSV budget |
| `GET` | `/projects/{id}/data-quality` | Data quality report |
| `GET` | `/projects/{id}/work-items` | List work items (filterable) |
| `GET` | `/projects/{id}/milestones` | List milestones |
| `GET` | `/projects/{id}/dependencies` | List dependencies |
| `GET` | `/projects/{id}/risks` | List active risks |
| `GET` | `/projects/{id}/risk-summary` | Risk category breakdown |
| `POST` | `/projects/{id}/evaluate` | Trigger risk evaluation |
| `GET/PUT` | `/projects/{id}/thresholds` | View/update thresholds |
| `GET` | `/projects/{id}/actions` | List actions |
| `GET` | `/projects/{id}/audit` | Audit trail |
| `GET` | `/projects/{id}/summary/weekly` | Weekly risk summary |
| `GET` | `/projects/{id}/snapshots` | Project snapshots |
| `GET` | `/risks/{id}` | Risk detail (with evidence, timeline, recommendations) |
| `GET` | `/risks/{id}/recommendations` | Recommendations for a risk |
| `POST` | `/risks/{id}/outcome` | Record outcome |
| `POST` | `/risks/{id}/feedback` | Submit alert feedback |
| `POST` | `/recommendations/{id}/approve` | Approve recommendation |
| `POST` | `/recommendations/{id}/modify` | Modify and approve |
| `POST` | `/recommendations/{id}/dismiss` | Dismiss with reason |
| `POST` | `/recommendations/{id}/snooze` | Snooze for duration |
| `PATCH` | `/actions/{id}` | Update action |
| `POST` | `/actions/{id}/complete` | Mark action complete |
| `GET` | `/admin/health` | System health check |
| `GET` | `/admin/status` | Service status (db, ollama, scheduler) |

### Response Format

All API responses follow a consistent envelope:

```
Success:
{
  "data": { ... },
  "meta": { "page": 1, "per_page": 20, "total": 45 }
}

Error:
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [ ... ]
  }
}
```

### Pagination

List endpoints use cursor-based or offset pagination:

```
GET /api/v1/projects/{id}/work-items?page=1&per_page=20&status=open&sort=-due_date
```

---

# 5. Database Architecture

## Engine

PostgreSQL 16 with pgvector extension.

Single database instance serving both relational data and vector embeddings.

## Schema Design

### Entity-Relationship Overview

```
Project ──< DataSource
Project ──< Milestone
Project ──< WorkItem ──< Dependency (self-referencing via source/target)
Project ──< Team ──< TeamMember
Project ──< RiskEvent ──< RiskSignal
                       ──< Evidence
                       ──< Recommendation ──< Action
                       ──< RiskHistory
                       ──< Outcome
                       ──< Feedback
Project ──< BudgetRecord
Project ──< ProjectSnapshot
Project ──< DataQualityCheck
Project ──< RiskThreshold
Project ──< AuditLog
Project ──< SyncJob
```

### Core Tables

#### projects

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| name | VARCHAR(255) | Required |
| description | TEXT | Optional |
| project_type | VARCHAR(50) | Default: "software" |
| status | VARCHAR(20) | active / paused / archived |
| health | VARCHAR(20) | green / yellow / orange / red (computed) |
| created_at | TIMESTAMPTZ | Auto |
| updated_at | TIMESTAMPTZ | Auto |

#### data_sources

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| project_id | UUID | FK → projects |
| source_type | VARCHAR(30) | github / csv_budget |
| config | JSONB | Connection config (encrypted tokens) |
| status | VARCHAR(20) | connected / syncing / error / disconnected |
| last_synced_at | TIMESTAMPTZ | Nullable |
| created_at | TIMESTAMPTZ | Auto |

#### work_items

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| project_id | UUID | FK → projects |
| external_id | VARCHAR(100) | ID from source system (for dedup) |
| source_type | VARCHAR(30) | Which connector created it |
| title | VARCHAR(500) | |
| description | TEXT | |
| status | VARCHAR(30) | open / in_progress / done / closed |
| priority | VARCHAR(20) | low / medium / high / critical |
| item_type | VARCHAR(30) | task / bug / feature / decision |
| assignee | VARCHAR(200) | |
| labels | JSONB | Array of labels |
| created_at | TIMESTAMPTZ | When created in source system |
| updated_at | TIMESTAMPTZ | Last update in source system |
| due_date | DATE | Nullable |
| completed_at | TIMESTAMPTZ | Nullable |
| cycle_time_hours | FLOAT | Computed: completed_at - created_at |

#### milestones

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| project_id | UUID | FK → projects |
| external_id | VARCHAR(100) | |
| title | VARCHAR(255) | |
| target_date | DATE | |
| status | VARCHAR(20) | open / closed |
| completion_percent | FLOAT | 0.0 – 100.0, computed from work items |
| created_at | TIMESTAMPTZ | |

#### dependencies

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| project_id | UUID | FK → projects |
| source_item_id | UUID | FK → work_items (the blocked item) |
| target_item_id | UUID | FK → work_items (the blocker) |
| dependency_type | VARCHAR(30) | blocks / depends_on / related |
| status | VARCHAR(20) | active / resolved |
| detected_at | TIMESTAMPTZ | |
| resolved_at | TIMESTAMPTZ | Nullable |

#### risk_events

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| project_id | UUID | FK → projects |
| category | VARCHAR(30) | schedule / dependency / scope / capacity / quality / budget / decision |
| title | VARCHAR(500) | Human-readable risk title |
| severity | VARCHAR(20) | low / medium / high / critical |
| confidence | VARCHAR(20) | low / medium / high |
| score | FLOAT | Composite propensity score |
| status | VARCHAR(20) | new / active / mitigated / resolved / closed / dismissed |
| affected_milestone_id | UUID | FK → milestones (nullable) |
| detected_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |
| agent_explanation | TEXT | AI-generated explanation (nullable, populated after investigation) |
| agent_investigated_at | TIMESTAMPTZ | Nullable |

#### risk_signals

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| risk_event_id | UUID | FK → risk_events |
| signal_type | VARCHAR(50) | e.g., "overdue_tasks", "blocked_items" |
| category | VARCHAR(30) | |
| value | FLOAT | Measured value |
| threshold | FLOAT | Threshold that was crossed |
| severity | VARCHAR(20) | |
| details | JSONB | Additional context (item IDs, dates) |
| detected_at | TIMESTAMPTZ | |

#### evidence

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| risk_event_id | UUID | FK → risk_events |
| source_type | VARCHAR(30) | work_item / dependency / milestone / budget / agent |
| reference_id | UUID | FK to the source record (nullable) |
| reference_label | VARCHAR(200) | Human-readable reference |
| explanation | TEXT | What this evidence indicates |
| relevance_score | FLOAT | 0.0 – 1.0 |

#### recommendations

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| risk_event_id | UUID | FK → risk_events |
| action_description | TEXT | What to do |
| rationale | TEXT | Why this action helps |
| suggested_owner | VARCHAR(200) | |
| urgency | VARCHAR(20) | immediate / today / this_week / optional |
| status | VARCHAR(20) | pending / approved / modified / dismissed / snoozed |
| decision_reason | TEXT | Nullable — reason if modified/dismissed |
| decided_at | TIMESTAMPTZ | Nullable |
| snooze_until | TIMESTAMPTZ | Nullable |

#### actions

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| recommendation_id | UUID | FK → recommendations |
| project_id | UUID | FK → projects |
| description | TEXT | |
| owner | VARCHAR(200) | |
| due_date | DATE | |
| status | VARCHAR(20) | pending / in_progress / completed / overdue |
| completed_at | TIMESTAMPTZ | Nullable |
| created_at | TIMESTAMPTZ | |

#### outcomes

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| risk_event_id | UUID | FK → risk_events |
| result | VARCHAR(20) | yes / partially / no / not_sure |
| feedback_comment | TEXT | Nullable |
| recorded_at | TIMESTAMPTZ | |

#### audit_logs

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| project_id | UUID | FK → projects |
| event_type | VARCHAR(50) | risk_detected / recommendation_approved / action_created / etc. |
| entity_type | VARCHAR(30) | risk_event / recommendation / action |
| entity_id | UUID | |
| details | JSONB | Event-specific data |
| created_at | TIMESTAMPTZ | |

#### embeddings

| Column | Type | Notes |
|---|---|---|
| id | UUID | Primary key |
| project_id | UUID | FK → projects |
| source_type | VARCHAR(30) | work_item / milestone / risk_event |
| source_id | UUID | FK to source record |
| content | TEXT | Text that was embedded |
| embedding | VECTOR(384) | pgvector column (dimension depends on model) |
| created_at | TIMESTAMPTZ | |

### Indexes

- `work_items`: composite on `(project_id, status)`, index on `due_date`, index on `external_id`
- `risk_events`: composite on `(project_id, status, severity)`, index on `detected_at`
- `dependencies`: composite on `(project_id, status)`, indexes on `source_item_id` and `target_item_id`
- `embeddings`: IVFFlat or HNSW index on `embedding` column for approximate nearest-neighbor search
- `audit_logs`: composite on `(project_id, created_at)`

---

# 6. Connector Architecture

## Design Pattern

All connectors implement a common abstract interface. This makes it possible to add new data sources without modifying the risk engine or service layer.

```
             ┌───────────────────┐
             │  BaseConnector    │  abstract
             │                   │
             │  + connect()      │  Validate credentials and connectivity
             │  + sync()         │  Fetch and normalize data
             │  + status()       │  Report connection health
             │  + disconnect()   │  Clean up
             └─────────┬─────────┘
                       │
          ┌────────────┼────────────┐
          │                         │
┌─────────┴──────────┐  ┌──────────┴─────────┐
│  GitHubConnector   │  │ CSVBudgetConnector  │
│                    │  │                     │
│  Issues → WorkItem │  │  CSV → BudgetRecord │
│  Milestones → ...  │  │                     │
│  PRs → ...         │  │                     │
│  Refs → Dependency │  │                     │
└────────────────────┘  └─────────────────────┘
```

### Connector Contract

Every `sync()` call must:

1. Fetch data from the external source (incremental if possible).
2. Normalize records into the internal data model.
3. Upsert records using `external_id` for deduplication.
4. Return a `SyncResult` with counts (created, updated, errors).
5. Handle API failures gracefully (retry transient errors, log permanent errors).

### Adding a New Connector (Future)

To add a Jira connector:

1. Create `connectors/jira.py` implementing `BaseConnector`.
2. Map Jira issues → `WorkItem`, sprints → `Milestone`, links → `Dependency`.
3. Register the connector type in `DataSource.source_type`.
4. No changes needed in the risk engine, agent, or frontend.

---

# 7. Risk Engine Architecture

## Design

The risk engine is a deterministic computation layer. It contains no LLM calls. It evaluates project data against configurable rules and produces structured risk signals.

```
┌──────────────────────────────────────────┐
│           RiskEngineService              │
│                                          │
│  1. Load project state from DB           │
│  2. Load configured thresholds           │
│  3. Run all enabled rules                │
│  4. Collect signals                      │
│  5. Score risks per category             │
│  6. Aggregate to overall project risk    │
│  7. Create/update RiskEvent records      │
│  8. Trigger agent for material risks     │
└──────────────────────────────────────────┘
         │
         │ runs each
         ↓
┌──────────────────────────────────────────┐
│         BaseRiskRule (abstract)           │
│                                          │
│  + category: str                         │
│  + signal_type: str                      │
│  + evaluate(state, thresholds) → signals │
└──────────────────────────────────────────┘
         │
    implemented by
         │
    ┌────┼─────┬──────┬──────┬──────┬──────┐
    │    │     │      │      │      │      │
  Schedule  Dep   Scope  Cap  Quality Budget Decision
  Rules    Rules  Rules  Rules Rules  Rules  Rules
```

### Scoring Model

```
Category Score = Σ (signal_severity_weight × signal_value / signal_threshold)

Project Risk = Σ (category_weight × category_score)

Risk Level:
  score < 0.3  → Low
  score < 0.6  → Medium
  score < 0.8  → High
  score >= 0.8 → Critical

Confidence:
  data_quality > 80% AND signals > 3 → High
  data_quality > 50% AND signals > 1 → Medium
  otherwise → Low
```

Category weights default to equal (1/7 each) but are configurable per project.

### Material Risk Threshold

A risk event triggers agent investigation when:

- Severity is **High** or **Critical**, OR
- Severity is **Medium** AND confidence is **High**, OR
- Multiple categories contribute signals simultaneously (compound risk)

---

# 8. Agent Architecture

## Framework

LangGraph stateful workflow with explicit nodes, edges, and a shared state object.

## Workflow Graph

```
                    ┌──────────┐
                    │  START   │
                    └────┬─────┘
                         │
                         ↓
                  ┌──────────────┐
                  │  investigate │  Assemble context, initial reasoning
                  └──────┬───────┘
                         │
                         ↓
               ┌─────────────────────┐
               │  retrieve_evidence  │  pgvector search + DB queries
               └─────────┬───────────┘
                         │
                         ↓
                  ┌──────────────┐
                  │   analyze    │  Root-cause identification
                  └──────┬───────┘
                         │
                         ↓
                  ┌──────────────┐
                  │  recommend   │  Generate mitigation actions
                  └──────┬───────┘
                         │
                         ↓
                  ┌──────────────┐
                  │   review     │  Quality check / hallucination guard
                  └──────┬───────┘
                         │
                    ┌────┴────┐
                    │  PASS?  │
                    └────┬────┘
                   yes/  │  \no
                   ↓     │    ↓
              ┌────────┐ │ ┌─────────┐
              │  SAVE  │ │ │ RETRY   │ (max 1 retry, then save with low confidence)
              └────────┘ │ └─────────┘
                         ↓
                      ┌──────┐
                      │ END  │
                      └──────┘
```

## State Object

The `InvestigationState` carries all data through the graph:

```
InvestigationState:
  risk_event_id          # Which risk triggered this investigation
  risk_signals           # Structured signals from the risk engine
  project_context        # Related work items, milestones, dependencies
  retrieved_evidence     # Evidence from pgvector and DB queries
  contributing_factors   # Root-cause analysis output
  explanation            # Human-readable risk explanation
  recommendations        # List of mitigation actions
  confidence             # Agent's confidence in the analysis
  quality_check_result   # Pass / fail from review node
  retry_count            # Number of retries (max 1)
  error                  # Error message if pipeline fails
```

## LLM Service Abstraction

```
LLMService:
  + generate(prompt, system_prompt, temperature) → str
  + embed(text) → list[float]
  + provider: "ollama" | "openai"

OllamaProvider:
  endpoint: http://ollama:11434
  model: configurable (default: llama3.1 or equivalent)
  no API key required

OpenAIProvider:
  endpoint: https://api.openai.com/v1  (or compatible)
  model: configurable
  API key from environment
```

The provider is selected via the `LLM_PROVIDER` environment variable.

## Prompt Management

All prompts are stored as Markdown template files in `agent/prompts/`, not hardcoded in Python. This makes it easy to iterate on prompt quality without changing code.

Each prompt file contains:

- System instructions
- Expected input format
- Expected output format (structured)
- Constraints (cite evidence, no unsupported claims)
- Examples

---

# 9. Frontend Architecture

## Rendering Strategy

- **Server components** for data-fetching pages (dashboard, risk list).
- **Client components** for interactive elements (approval controls, forms, charts).
- **API client** on the client side for mutations and real-time state updates.

## Page Structure

| Route | Page | Primary Question Answered |
|---|---|---|
| `/projects` | Project list | Which projects am I monitoring? |
| `/projects/new` | New project wizard | How do I connect my project? |
| `/projects/[id]` | Project dashboard | What needs my attention today? |
| `/projects/[id]/risks` | Risk list | What are all the current risks? |
| `/projects/[id]/risks/[riskId]` | Risk detail | Why was this flagged and what should I do? |
| `/projects/[id]/actions` | Action tracking | What actions are open, completed, or overdue? |
| `/projects/[id]/summary` | Weekly summary | How did risks change this week? |
| `/projects/[id]/audit` | Audit trail | What decisions were made and when? |
| `/projects/[id]/settings` | Settings | What am I monitoring and at what sensitivity? |

## State Management

- **Server state:** React Server Components fetch data on the server. No client-side cache for initial loads.
- **Client mutations:** Custom hooks using `fetch` with optimistic updates where appropriate.
- **No global state library** in MVP. React context for theme and layout state only. Add SWR or TanStack Query only if client-side caching becomes necessary.

## Component Design

- **Atomic components** from shadcn/ui: Button, Card, Badge, Dialog, Table, Dropdown, Tooltip, etc.
- **Domain components** compose atomic components: RiskCard, EvidenceList, ApprovalControls, HealthIndicator.
- **Page components** compose domain components into complete views.

Components never call the API directly. They receive data as props or use custom hooks from `lib/hooks/`.

---

# 10. Data Flow

## Sync Flow

```
Scheduler triggers sync
         │
         ↓
SyncService.sync_project(project_id)
         │
         ↓
Load DataSources for project
         │
    ┌────┴─────────────────────┐
    │                          │
    ↓                          ↓
GitHubConnector.sync()    CSVBudgetConnector.sync()
    │                          │
    ↓                          ↓
Upsert WorkItems          Upsert BudgetRecords
Upsert Milestones
Upsert Dependencies
    │                          │
    └──────────┬───────────────┘
               │
               ↓
    DataQualityService.evaluate(project_id)
               │
               ↓
    Update data_quality score
               │
               ↓
    RiskEngineService.evaluate(project_id)
               │
               ↓
    Create/update RiskEvents
               │
               ↓
    For each material risk:
        AgentService.investigate(risk_event_id)  (async)
               │
               ↓
    Update risk with explanation + recommendations
```

## User Decision Flow

```
PM views risk detail page
         │
         ↓
PM clicks "Approve" on a recommendation
         │
         ↓
Frontend: POST /api/v1/recommendations/{id}/approve
         │
         ↓
RecommendationService.approve(id)
         │
         ├─→ Update recommendation.status = "approved"
         ├─→ Create Action record
         └─→ Create AuditLog entry
         │
         ↓
Response: { action_id, status: "created" }
         │
         ↓
PM sees action in the Actions list
         │
         ↓
PM completes action: POST /api/v1/actions/{id}/complete
         │
         ↓
ActionService.complete(id)
         │
         ├─→ Update action.status = "completed"
         └─→ Create AuditLog entry
```

---

# 11. Infrastructure

## Docker Compose Services

| Service | Image | Port | Purpose |
|---|---|---|---|
| `db` | postgres:16 + pgvector | 5432 | Database |
| `backend` | Custom (Python) | 8000 | FastAPI API server |
| `frontend` | Custom (Node) | 3000 | Next.js web server |
| `ollama` | ollama/ollama | 11434 | Local LLM inference |

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `DATABASE_URL` | backend | PostgreSQL connection string |
| `GITHUB_TOKEN` | backend | Default GitHub PAT (can also be per-source) |
| `LLM_PROVIDER` | backend | "ollama" or "openai" |
| `LLM_MODEL` | backend | Model name (e.g., "llama3.1") |
| `OLLAMA_HOST` | backend | Ollama endpoint (default: http://ollama:11434) |
| `OPENAI_API_KEY` | backend | Optional, for cloud LLM |
| `SYNC_INTERVAL_MINUTES` | backend | Default sync interval (e.g., 60) |
| `LOG_LEVEL` | backend | DEBUG / INFO / WARNING / ERROR |
| `NEXT_PUBLIC_API_URL` | frontend | Backend API URL |

## Networking

- All services on a single Docker network.
- Frontend proxies API calls to backend.
- Ollama is accessible only from backend (not exposed externally).
- PostgreSQL is accessible only from backend.

## Volumes

- `postgres_data`: Persistent database storage.
- `ollama_models`: Cached model files.

---

# 12. Security Architecture

## Credential Management

- All secrets in environment variables, loaded via `.env` file (not committed to git).
- GitHub tokens stored in `data_sources.config` column, encrypted using Fernet symmetric encryption.
- Encryption key stored as environment variable `ENCRYPTION_KEY`.

## API Security

- MVP uses API-key authentication for simplicity (single-user system).
- All input validated via Pydantic schemas.
- SQL injection prevented by SQLAlchemy parameterized queries.
- File upload (CSV) validated for content type and parsed safely.

## Data Privacy

- No employee personal data stored beyond project-role identifiers (assignee names for work items).
- LLM prompts include only project-level data: task titles, statuses, dates, dependency relationships.
- LLM prompts never include: personal messages, browsing data, salary information.
- Agent prompts include explicit instruction: "Do not evaluate individual employee performance."

## Container Security

- Docker images use non-root users.
- Only necessary ports are exposed.
- Ollama and PostgreSQL are not exposed to the host network in production.

---

# 13. Observability

## Logging

**Library:** structlog (JSON format)

Every log entry includes:

- `timestamp` (ISO 8601)
- `level` (info, warning, error)
- `event` (human-readable event name)
- `correlation_id` (request-scoped)
- `project_id` (when applicable)
- Context-specific fields

### Key Events Logged

| Event | Level | When |
|---|---|---|
| `sync.started` | info | Sync job begins |
| `sync.completed` | info | Sync job finishes (includes counts) |
| `sync.failed` | error | Sync job fails (includes error) |
| `risk.detected` | info | New risk event created |
| `risk.severity_changed` | info | Risk severity changed |
| `agent.investigation.started` | info | Agent pipeline begins |
| `agent.investigation.completed` | info | Agent pipeline finishes |
| `agent.investigation.failed` | error | Agent pipeline fails |
| `agent.llm_call` | debug | Individual LLM call (includes token count) |
| `recommendation.approved` | info | User approved recommendation |
| `recommendation.dismissed` | info | User dismissed recommendation |
| `action.created` | info | Action created from recommendation |
| `action.completed` | info | Action marked complete |
| `outcome.recorded` | info | Outcome feedback recorded |

## Audit Trail

Separate from application logs. Stored in the `audit_logs` database table. Provides a user-facing, queryable record of all risk-related decisions.

## Health Check

`GET /api/v1/admin/health` returns:

```
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "ollama": "connected",
    "scheduler": "running"
  },
  "uptime_seconds": 3600
}
```

---

# 14. Scalability Considerations

The MVP is designed for single-project or small multi-project use. The following decisions support future scaling without requiring a rewrite:

| Concern | MVP Approach | Future Scale Path |
|---|---|---|
| Multiple projects | Single database, queries scoped by `project_id` | Tenant isolation via schema or separate databases |
| Large work item counts | Standard PostgreSQL indexes | Partitioning by project, read replicas |
| Agent throughput | Sequential investigation per risk | Background task queue (Celery/RQ) |
| LLM costs | Local Ollama for development; selective invocation | Model routing, caching, smaller specialized models |
| Real-time updates | Polling from frontend | WebSocket or SSE for live updates |
| User management | Single-user MVP | Add auth (NextAuth), RBAC |
| Connector count | GitHub + CSV | Plugin registry for community connectors |

---

# 15. Key Architecture Decisions Record

| # | Decision | Rationale | Alternatives Rejected |
|---|---|---|---|
| ADR-01 | Modular monolith, not microservices | Solo developer; simpler to build, deploy, debug | Microservices (too much infra overhead) |
| ADR-02 | PostgreSQL for both relational and vector data | Reduces operational complexity; pgvector is sufficient at MVP scale | Separate Pinecone/Weaviate (unnecessary) |
| ADR-03 | Rules-first risk detection, LLM second | Cheaper, faster, explainable, works without LLM | LLM-only detection (expensive, unreliable) |
| ADR-04 | Single LangGraph workflow, not multi-agent swarm | Simpler to debug and evaluate; sufficient for MVP | CrewAI / AutoGen multi-agent (overengineered) |
| ADR-05 | APScheduler for periodic jobs | In-process, no extra infrastructure | Celery + Redis (too heavyweight for MVP) |
| ADR-06 | Prompts as Markdown files, not hardcoded | Easy to iterate, version, and review | Inline strings (harder to maintain) |
| ADR-07 | No frontend state library | Server Components + custom hooks sufficient for MVP | Redux / Zustand (premature complexity) |
| ADR-08 | Fernet encryption for stored tokens | Standard symmetric encryption; simple to implement | Vault / KMS (enterprise-tier) |
| ADR-09 | API-key auth, not OAuth/SSO | Single-user MVP; add auth layer later | NextAuth / Auth0 (scope creep) |
| ADR-10 | Offset pagination, not cursor-based | Simpler for MVP list views | Cursor pagination (optimize later if needed) |
