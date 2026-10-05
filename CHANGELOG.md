# Changelog

All notable changes to RiskZen are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned

- Core data model for all 10 entities (Milestones, WorkItems, Dependencies, Teams, RiskEvents, Evidence, Recommendations, Actions, Outcomes, AuditLogs)
- GitHub connector and CSV budget importer
- Risk signal detection engine (7 categories)
- LangGraph agent investigation workflow
- Project health dashboard and UI screens

---

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
