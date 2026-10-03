# RiskZen

## AI-Powered Project Risk Early-Warning & Mitigation System

**Project type:** Agentic AI / Project Management Intelligence
**Initial domain:** Software and product-development projects
**Primary user:** Project Manager / Delivery Manager
**MVP objective:** Detect meaningful project risks earlier, explain why they are emerging, and recommend practical mitigation actions that a human manager can approve.

---

# 1. Product Definition

## 1.1 Problem

Project managers often discover important delivery risks late because project information is fragmented across task trackers, engineering systems, schedules, budgets, dependencies, quality records, and status reports.

The fundamental problem is:

> **Project teams lack a continuous mechanism for combining weak signals across project data, identifying emerging risks early, explaining their causes, and translating them into actionable interventions.**

The result is delayed intervention, reduced delivery flexibility, avoidable rework, schedule slippage, cost exposure, and management time spent collecting information rather than acting on it.

---

## 1.2 Product Vision

**RiskZen** is an evidence-driven AI early-warning system that continuously monitors project-level signals, detects emerging risks, investigates their likely causes, and recommends mitigation actions.

The system is designed as:

> **Rules + analytics first → agentic reasoning second → human-approved action third.**

It is **not** an autonomous project manager in the MVP.

---

# 2. Strategic Design Principles

The product will follow these principles:

### Project-level, not employee surveillance

The system evaluates project conditions rather than individual employee productivity.

It should detect:

* blocked work,
* dependency failures,
* cycle-time deterioration,
* scope volatility,
* workload imbalance,
* quality trends,
* decision delays.

It should not score employee commitment, rank developers, monitor keystrokes, or analyze private communications.

### Evidence before explanation

An AI explanation is generated only after structured signals and supporting project evidence are identified.

### Human authority

The agent may detect, investigate and recommend.

A human approves consequential actions.

### Cheap computation before expensive AI

Routine event processing uses deterministic rules and analytics.

LLM reasoning is triggered selectively for material or ambiguous risks.

### Data quality is a feature

The system explicitly reports what data is missing or unreliable.

### Outcome-based learning

The system records what happened after each intervention so future risk models can be improved.

---

# 3. MVP Goal

The MVP must prove one core hypothesis:

> **Can the system identify a meaningful project risk early enough, explain it clearly enough, and recommend an action useful enough that a project manager changes what they do?**

The MVP does not need to predict every project failure.

It needs to demonstrate a credible **risk-to-action loop**.

---

# 4. Target Users

## Primary user

### Project Manager / Delivery Manager

Needs:

* project health visibility,
* early warnings,
* evidence,
* root-cause analysis,
* actionable recommendations,
* concise prioritization.

Main constraint:

> The user cannot investigate dozens of alerts manually.

Therefore, alert relevance is more important than alert volume.

## Secondary users

* Engineering Managers
* Program Managers
* PMO / Portfolio Managers
* Project Sponsors
* Delivery Leads

## Supporting stakeholders

* Engineering teams
* Finance
* IT / Security
* Compliance / Legal
* Executives

---

# 5. Initial Scope

## In scope

The MVP will monitor:

1. Schedule
2. Dependencies
3. Scope volatility
4. Workload / capacity signals
5. Quality signals
6. Decision latency
7. Basic budget information

## Out of scope

The MVP will not:

* automatically reallocate employees,
* autonomously change deadlines,
* automatically change budgets,
* score individual employee performance,
* process private employee communications,
* make high-impact decisions without human approval,
* support every project industry,
* require custom model training,
* implement complex multi-agent swarms,
* build enterprise SSO/RBAC infrastructure,
* integrate dozens of systems.

---

# 6. Primary MVP User Journey

The complete MVP journey is:

> **Connect → Configure → Monitor → Detect → Investigate → Explain → Decide → Act → Track → Learn**

## Persona

**Project Manager:** Anita
**Project:** Customer Authentication Upgrade
**Team:** 7 people
**Systems:** GitHub + project tracker + CSV budget

---

## Step 1 — Connect Project

Anita creates a project and connects available sources.

Example:

```text
GitHub
Project Tracker
Budget CSV
```

The system imports the project.

It displays:

```text
Work items:          126
Milestones:            7
Dependencies:         18
Historical data:     30 days
Budget data:       Available
Data quality:         87%
```

The system also identifies missing information.

Example:

> Budget data is available only at monthly level; task-level cost analysis is unavailable.

---

## Step 2 — Configure Monitoring

Anita selects:

```text
Schedule
Dependencies
Quality
Scope
Capacity
Budget
```

She can accept recommended thresholds or configure them.

Example:

```text
Blocked-task warning:       3 days
Milestone-slip warning:    2 days
Scope-growth warning:     15%
```

---

## Step 3 — Continuous Monitoring

The system periodically:

1. collects new project events,
2. updates the project state,
3. calculates risk signals,
4. compares signals with thresholds and trends,
5. stores risk events.

Routine processing occurs without an LLM.

---

## Step 4 — Risk Signal Appears

Example:

```text
API Integration #1       blocked 5 days
API Integration #2       blocked 4 days
Upstream dependency      3 days late
QA defects               reopened twice
Milestone buffer         9 working days
```

The rules engine creates:

**Risk Event R-104**

> Potential high schedule risk.

The system has detected a signal but has not yet assumed a root cause.

---

## Step 5 — Agent Investigation

The agent is triggered because the risk crosses a configured significance threshold.

It retrieves:

* related tasks,
* dependency history,
* milestone data,
* defect history,
* recent work changes,
* relevant project documentation,
* previous related risks.

It determines that the strongest contributing factors are:

1. delayed upstream dependency,
2. downstream integration blockage,
3. increasing QA rework.

---

## Step 6 — Risk Alert

The PM sees:

### High Schedule Risk — Authentication Integration

**Potential impact**

The authentication milestone may slip if the upstream dependency remains unresolved.

**Evidence**

* Two integration tasks blocked beyond threshold.
* Upstream dependency is overdue.
* Related work has increasing cycle time.
* QA rework has increased.
* Remaining milestone buffer is limited.

**Recommended actions**

1. Escalate the upstream dependency.
2. Conduct a backend/QA integration review.
3. Split remaining integration work into independent deliverables.
4. Reassess milestone scope if dependency remains unresolved.

---

## Step 7 — Human Decision

The user can:

```text
Approve
Modify
Dismiss
Snooze
```

Anita selects **Modify** and changes the dependency escalation owner.

The system records the decision.

---

## Step 8 — Action Creation

The system proposes:

```text
Resolve authentication dependency
Owner: Platform Team
Due: Today

Integration review
Participants: Backend + QA + DevOps

Split integration work
Owner: Backend Lead
Due: Tomorrow
```

The user confirms the approved actions.

Initially, the system should **propose** action creation rather than silently executing it.

---

## Step 9 — Risk Reassessment

The next day:

* dependency is resolved,
* blocked work resumes,
* QA retesting starts.

The system recalculates the risk.

```text
HIGH
  ↓
MEDIUM
```

It explains:

> Risk decreased following resolution of the upstream dependency and resumption of blocked integration work.

---

## Step 10 — Outcome Feedback

At milestone completion, the system asks:

> Did the recommended intervention materially help?

Options:

```text
Yes
Partially
No
Not sure
```

The PM can add a comment.

This produces:

```text
Risk detected
      ↓
Recommendation
      ↓
Human intervention
      ↓
Risk change
      ↓
Outcome feedback
```

This feedback becomes part of the system's evaluation dataset.

---

# 7. Core Functional Requirements

## FR-01: Project onboarding

The system shall allow a user to:

* create a project,
* connect supported data sources,
* view connection status,
* view available data coverage.

## FR-02: Data normalization

The system shall transform source data into a common project model.

### Core entities

```text
Project
Milestone
WorkItem
Dependency
Team
RiskEvent
Evidence
Recommendation
Action
Outcome
```

## FR-03: Data quality assessment

The system shall calculate and display data-quality indicators.

Examples:

* missing dates,
* stale work items,
* incomplete dependencies,
* missing budget data,
* inconsistent status information.

## FR-04: Risk signal detection

The system shall detect configurable signals across:

* schedule,
* dependencies,
* scope,
* capacity,
* quality,
* budget,
* decisions.

## FR-05: Risk scoring

Each material risk shall receive:

* severity,
* signal score,
* confidence,
* affected component,
* status.

The initial system must avoid presenting the score as a statistically calibrated probability.

Use terminology such as:

> Low / Medium / High / Critical

and:

> Low / Medium / High confidence.

## FR-06: Agent investigation

For material risks, the agent shall:

1. inspect relevant structured signals,
2. retrieve supporting evidence,
3. identify contributing factors,
4. explain the risk,
5. identify affected milestones/work,
6. propose mitigation.

## FR-07: Evidence display

Every material alert shall show the evidence supporting the warning.

## FR-08: Recommendations

Each material risk should provide practical recommended actions with:

* rationale,
* suggested owner,
* suggested urgency,
* expected purpose.

## FR-09: Human approval

Users shall be able to:

* approve,
* modify,
* dismiss,
* snooze,
* assign,
* comment.

## FR-10: Action tracking

Approved actions shall have:

* owner,
* due date,
* status,
* source risk,
* completion state.

## FR-11: Outcome tracking

The system shall record:

* risk status before action,
* action performed,
* risk status afterward,
* user feedback,
* eventual outcome.

## FR-12: Audit trail

The system shall record:

* detected risk,
* evidence used,
* agent recommendation,
* user decision,
* action,
* outcome.

---

# 8. Risk Detection Model

## Initial risk categories

### Schedule

Signals include:

* overdue tasks,
* milestone slippage,
* increasing cycle time,
* aging work,
* declining completion rate.

### Dependencies

Signals include:

* blocked tasks,
* overdue upstream dependencies,
* dependency concentration,
* cross-team handoff delays.

### Scope

Signals include:

* new work entering active cycles,
* requirement churn,
* priority changes,
* reopened work.

### Capacity

Signals include:

* demand exceeding planned capacity,
* excessive work in progress,
* workload concentration,
* bottlenecks.

### Quality

Signals include:

* defect growth,
* reopened issues,
* failed builds,
* increasing test failures,
* incident trends.

### Budget

Initial MVP support can use:

* planned vs actual spend,
* burn-rate changes,
* forecast variance.

### Decision latency

Signals include:

* overdue approvals,
* unresolved decisions,
* long-running blockers,
* delayed stakeholder responses.

---

# 9. Agent Workflow

The MVP should implement one orchestrated workflow rather than an unnecessarily complex multi-agent system.

```text
Data Sources
     ↓
Collector
     ↓
Normalizer
     ↓
Risk Signal Engine
     ↓
Material Risk?
     ↓
Investigator
     ↓
Evidence Retrieval
     ↓
Root-Cause Analysis
     ↓
Recommendation Generation
     ↓
Evidence / Quality Check
     ↓
Human Review
     ↓
Approved Action
     ↓
Outcome Tracking
```

The agent should not independently modify project state without approval.

---

# 10. Technical Architecture

## Frontend

* Next.js
* TypeScript
* Tailwind CSS
* component library such as shadcn/ui

## Backend

* Python
* FastAPI

## Database

* PostgreSQL

## Vector storage

* pgvector

Use PostgreSQL for both operational and vector data in the MVP rather than adding a separate vector database.

## Agent orchestration

* LangGraph or equivalent stateful workflow framework

## Local model option

* Ollama-compatible local model deployment

## Infrastructure

* Docker
* Docker Compose

## Observability

Initially:

* structured application logs,
* request tracing,
* agent execution logs,
* audit records.

---

# 11. MVP Data Model

A simplified schema:

```text
Project
 ├── id
 ├── name
 ├── type
 ├── status
 └── created_at

WorkItem
 ├── id
 ├── project_id
 ├── status
 ├── priority
 ├── assignee
 ├── created_at
 ├── due_date
 └── completed_at

Dependency
 ├── id
 ├── source_work_item
 ├── target_work_item
 └── status

Milestone
 ├── id
 ├── project_id
 ├── target_date
 ├── status
 └── completion_percent

RiskEvent
 ├── id
 ├── project_id
 ├── category
 ├── severity
 ├── confidence
 ├── detected_at
 ├── status
 └── score

Evidence
 ├── id
 ├── risk_id
 ├── source
 ├── reference
 └── explanation

Recommendation
 ├── id
 ├── risk_id
 ├── action
 ├── rationale
 └── status

Action
 ├── id
 ├── recommendation_id
 ├── owner
 ├── due_date
 └── status

Outcome
 ├── id
 ├── risk_id
 ├── result
 ├── feedback
 └── recorded_at
```

---

# 12. MVP User Interface

## Dashboard

The dashboard should answer:

> **What requires my attention today?**

Display:

```text
Project Health
     ↓
Top Emerging Risks
     ↓
Affected Milestones
     ↓
Dependency Bottlenecks
     ↓
Overdue Risk Actions
     ↓
Recent Risk Changes
```

## Risk detail page

Must answer:

> Why was this flagged?

Display:

1. Risk
2. Severity
3. Confidence
4. Impact
5. Evidence
6. Contributing factors
7. Timeline
8. Recommendations
9. Decision controls
10. Action history
11. Outcome

---

# 13. Non-Functional Requirements

## Explainability

A user should be able to trace:

**risk → signals → evidence → explanation → recommendation**

## Privacy

Use least-privilege access.

Collect project data required for risk monitoring and avoid unrelated personal information.

## Reliability

The monitoring pipeline should tolerate:

* API failures,
* partial data,
* duplicate events,
* delayed updates.

## Security

Minimum requirements:

* encrypted credentials,
* secret management,
* authenticated APIs,
* access controls,
* audit logs.

## Maintainability

Connectors and risk rules should be modular.

Adding a new project-management system should not require rewriting the core risk engine.

---

# 14. MVP Success Criteria

The MVP should achieve the following pilot targets:

| Measure                       |          Initial target |
| ----------------------------- | ----------------------: |
| Relevant alerts               |                    ≥70% |
| Actionable recommendations    |                    ≥60% |
| Critical-risk false positives |                    <30% |
| Manager action rate           |                    ≥60% |
| Investigation time reduction  |                    ≥50% |
| Data freshness                | >90% within defined SLA |
| Risk-action traceability      |                    >90% |
| User usefulness rating        |                    ≥4/5 |

These are **validation targets**, not guaranteed outcomes.

The most important success measure is:

> **Material risks are identified earlier and lead to useful human action.**

---

# 15. Evaluation Framework

## Technical evaluation

Measure:

* signal precision,
* signal recall,
* false-positive rate,
* detection lead time.

## AI evaluation

Review:

* factual grounding,
* evidence completeness,
* root-cause accuracy,
* recommendation relevance,
* unsupported assertions.

## User evaluation

Measure:

* perceived usefulness,
* trust,
* time saved,
* action rate,
* dismissal rate.

## Outcome evaluation

Measure:

* risk reduction,
* mitigation completion,
* milestone outcomes,
* avoidable delays,
* rework indicators.

---

# 16. Baseline

Before active pilot deployment, reconstruct several weeks of historical project data where possible.

For previous risks record:

```text
Risk type
First observable signal
Date identified by team
Date escalated
Impact
Intervention
Outcome
```

The key question is:

> **Would RiskZen have detected the risk earlier than the existing review process?**

---

# 17. Implementation Plan

## Phase 0 — Validation

**1 week**

Outputs:

* stakeholder interviews,
* top risk taxonomy,
* data-source inventory,
* pilot project selected.

Exit condition:

At least three important risk patterns have observable leading indicators.

---

## Phase 1 — Data Foundation

**1–2 weeks**

Build:

* database,
* normalized schema,
* ingestion layer,
* GitHub connector,
* CSV importer,
* data-quality checks.

Output:

> Unified project state.

---

## Phase 2 — Risk Engine

**2 weeks**

Build:

* schedule rules,
* dependency rules,
* scope rules,
* quality rules,
* capacity rules,
* initial budget rules.

Output:

> Working risk detection without an LLM.

---

## Phase 3 — Agentic Investigation

**2 weeks**

Build:

* agent workflow,
* evidence retrieval,
* explanation generation,
* recommendation generation,
* human-review controls.

Output:

> Evidence-backed risk alert.

---

## Phase 4 — Dashboard

**1–2 weeks**

Build:

* project dashboard,
* risk cards,
* risk detail page,
* action interface,
* feedback interface.

Output:

> Complete MVP user journey.

---

## Phase 5 — Evaluation

**1 week**

Run:

* historical replay,
* alert evaluation,
* explanation review,
* recommendation review.

Output:

> Measured baseline performance.

---

## Phase 6 — Pilot

**6–8 weeks**

Use:

* one real software project, or
* two to three small projects.

Pilot stages:

```text
Week 1    Baseline
Week 2    Integration
Week 3    Silent monitoring
Week 4    Tuning
Weeks 5–7 Live alerts
Week 8    Evaluation
```

---

# 18. MVP vs Future

| Capability                     | MVP | Future |
| ------------------------------ | :-: | :----: |
| Project dashboard              |  ✓  |        |
| Risk engine                    |  ✓  |        |
| Schedule risk                  |  ✓  |        |
| Dependency risk                |  ✓  |        |
| Scope risk                     |  ✓  |        |
| Quality risk                   |  ✓  |        |
| Capacity risk                  |  ✓  |        |
| Basic budget risk              |  ✓  |        |
| AI investigation               |  ✓  |        |
| Evidence-grounded explanations |  ✓  |        |
| Recommendations                |  ✓  |        |
| Human approval                 |  ✓  |        |
| Feedback loop                  |  ✓  |        |
| GitHub integration             |  ✓  |        |
| Additional connectors          |     |    ✓   |
| Predictive ML                  |     |    ✓   |
| Portfolio risk                 |     |    ✓   |
| Cross-project learning         |     |    ✓   |
| Autonomous bounded actions     |     |    ✓   |
| Resource optimization          |     |    ✓   |
| Enterprise controls            |     |    ✓   |

---

# 19. Pilot Design

## Participants

Prefer:

* one software team,
* 6–12 members,
* an active project,
* established digital project records.

## Duration

**8 weeks**

## Pilot objective

Determine whether the system provides:

1. earlier risk detection,
2. sufficiently accurate explanations,
3. useful recommendations,
4. measurable management value.

---

# 20. Pilot Decision Rules

## Scale

Proceed to broader deployment when:

* alert relevance is consistently strong,
* users regularly act on useful recommendations,
* detection occurs earlier than the current process,
* technical reliability is acceptable.

## Modify

Change the system when:

* alerts are technically correct but operationally irrelevant,
* recommendations are generic,
* data quality is inadequate,
* users ignore alerts.

## Stop or redesign

Reconsider the product if:

* false positives dominate,
* users consistently dismiss alerts,
* project outcomes show no meaningful improvement,
* necessary data cannot be accessed reliably,
* privacy/security constraints cannot be addressed.

---

# 21. Risks and Mitigation

| Risk                             | Likelihood | Severity | Mitigation                          |
| -------------------------------- | ---------- | -------- | ----------------------------------- |
| Poor data quality                | High       | High     | Data-quality scoring                |
| Alert fatigue                    | High       | High     | Threshold tuning + prioritization   |
| AI hallucination                 | Medium     | High     | Evidence-grounded generation        |
| Employee surveillance perception | High       | High     | Project-level monitoring only       |
| Privacy breach                   | Medium     | Critical | Least privilege + encryption        |
| Integration failures             | Medium     | Medium   | Connector abstraction + retries     |
| AI cost growth                   | Medium     | Medium   | Rule-first architecture             |
| User distrust                    | Medium     | High     | Explainability + human approval     |
| Incorrect autonomous action      | Low in MVP | Critical | No autonomous consequential actions |
| Domain generalization            | High       | Medium   | Start with software projects        |

---

# 22. Indicative Cost

## Development

Assuming existing development hardware:

| Category             |      Approximate cost |
| -------------------- | --------------------: |
| Open-source software |                    ₹0 |
| Local database       |                    ₹0 |
| Local inference      |                    ₹0 |
| Development hosting  |       ₹0–₹2,000/month |
| Domain               |      ₹800–₹1,500/year |
| Optional hosted LLM  | ₹2,000–₹10,000+/month |

## MVP estimate

**Local prototype:** approximately **₹0–₹5,000 incremental cost**

**Small cloud pilot:** approximately **₹5,000–₹20,000**

The largest likely costs are engineering effort, data preparation, evaluation, security and operational support rather than model inference.

---

# 23. Cost-Control Strategy

The processing hierarchy should be:

```text
Project Event
     ↓
Deterministic Rule
     ↓
Analytical Signal
     ↓
Material / Ambiguous Risk?
     ↓
AI Investigation
```

Not:

```text
Project Event
     ↓
LLM
```

This minimizes:

* compute cost,
* latency,
* unnecessary model calls,
* environmental footprint.

---

# 24. Sustainability and Scalability

## Technical scalability

The system should evolve from:

```text
One Project
     ↓
Multiple Projects
     ↓
Portfolio Risk
     ↓
Organization-Wide Risk Intelligence
```

through modular:

* connectors,
* risk models,
* agent workflows,
* policies,
* UI components.

## Product sustainability

Potential progression:

**Open-source prototype → hosted SaaS → enterprise deployment**

## Future intelligence

Once sufficient historical data exists:

**rules → calibrated predictive models → domain-specific forecasting**

Autonomous actions should only be introduced later and should remain bounded, auditable and reversible.

---

# 25. Innovation

The project's meaningful innovation is not simply the use of an LLM.

It is the combination of:

1. **Unified project-state modeling**
2. **Multidimensional risk-signal fusion**
3. **Evidence-grounded AI investigation**
4. **Action-oriented recommendations**
5. **Human-in-the-loop decisions**
6. **Outcome feedback**

The core differentiating loop is:

```text
Detect
  ↓
Investigate
  ↓
Explain
  ↓
Recommend
  ↓
Human decides
  ↓
Act
  ↓
Measure
  ↓
Learn
```

---

# 26. Final Product Definition

### Product

**RiskZen**

### Core promise

> Detect emerging project risks earlier, explain why they matter, and help managers act before avoidable project impact occurs.

### MVP user

Project Manager / Delivery Manager

### MVP environment

Software/product development

### Initial integrations

GitHub + project tracker + CSV budget

### Core risk areas

Schedule + dependencies + scope + capacity + quality + budget + decision latency

### Core AI function

Evidence-grounded investigation and mitigation recommendation

### Core human function

Approve, modify, dismiss and manage interventions

### Core success measure

**Earlier detection leading to useful action**

### MVP duration

Approximately **8–12 weeks of development**, followed by an **8-week pilot**

### MVP budget

Approximately **₹0–₹5,000 locally** or **₹5,000–₹20,000 for a small cloud pilot**, depending on infrastructure and model usage.

---

# 27. Final Positioning

The project should be presented as:

> **An explainable AI early-warning and intervention system for project delivery—not an autonomous replacement for project managers.**

The development maturity path is:

```text
Level 1 — Detect
       ↓
Level 2 — Correlate
       ↓
Level 3 — Investigate
       ↓
Level 4 — Recommend
       ↓
Level 5 — Human approval
       ↓
Level 6 — Learn from outcomes
       ↓
Level 7 — Calibrated prediction
       ↓
Level 8 — Bounded autonomous action
```

The MVP succeeds when it closes the first reliable loop:

> **Real project data → meaningful risk detected → evidence provided → useful recommendation → human action → measurable outcome.**