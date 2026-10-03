# Product Requirements Document

**Product:** RiskZen
**Document type:** Product Requirements Document (PRD)
**Purpose:** Define exactly what is being built and why. This document contains zero code. It is the single source of truth for MVP scope decisions.
**Date:** 2026-09-30
**Status:** Active

---

# 1. Product Statement

## What is this product?

RiskZen is an AI-powered early-warning system that monitors software projects for emerging delivery risks, explains why each risk is appearing, and recommends practical mitigation actions for human project managers to approve.

## What is it not?

It is not an autonomous project manager. It does not make decisions. It does not replace the PM. It does not monitor employees. It does not predict the future with statistical certainty.

## One-sentence value proposition

> Detect emerging project risks before they become costly failures, explain the evidence behind each warning, and recommend what to do about it — so the project manager acts earlier, not later.

---

# 2. Problem

## The problem we are solving

Project managers in software teams discover important delivery risks too late. By the time a risk becomes visible through conventional status reviews, intervention options have already narrowed and damage has already started.

## Why this problem exists

Project information is fragmented. Schedule data lives in one system, code activity in another, budget data in a spreadsheet, dependency knowledge in people's heads, and quality signals in CI/CD logs. No single tool correlates weak signals from all these sources into an early warning.

Managers rely on periodic reviews (usually weekly) to spot problems. Between reviews, risks grow undetected.

## Why this problem matters

Late risk detection leads to:

- avoidable schedule slippage,
- budget overruns from reactive rework,
- quality degradation from compressed timelines,
- cascading dependency failures,
- management time wasted collecting status instead of making decisions,
- team morale damage from preventable crises.

## The specific gap we are filling

| Current State | Desired State |
|---|---|
| PM discovers risk at weekly review | System surfaces risk as it emerges |
| PM manually correlates signals across tools | System automatically fuses signals from multiple sources |
| Risk explanation requires hours of investigation | System provides evidence and root-cause analysis in seconds |
| Mitigation is improvised under pressure | System recommends specific actions before the crisis |
| No record of what worked | System tracks outcomes to improve future detection |

---

# 3. Target Users

## Primary user: Project Manager / Delivery Manager

This person manages a software or product development project with a small-to-medium team (5–15 people). They use digital project tools (GitHub, a project tracker, spreadsheets). They conduct periodic reviews (weekly or biweekly). They are responsible for delivery, schedule, budget, and risk.

### What they need from this product

1. Know what requires their attention today — without collecting status manually.
2. Understand why a risk is appearing — with evidence, not just a score.
3. Know what to do about it — specific, practical recommendations.
4. Decide whether to act — approve, modify, or dismiss.
5. Track whether the intervention worked — outcome feedback.

### Their primary constraint

> They cannot spend hours validating every alert. If the system produces too many false positives or vague warnings, they will ignore it.

Therefore: **alert quality matters more than alert quantity.**

## Secondary users

| User | What they need |
|---|---|
| Engineering Manager | Dependency visibility, capacity risk, quality trends |
| Program Manager | Cross-project risk view (future, not MVP) |
| PMO / Portfolio Manager | Consistent risk reporting (future, not MVP) |

## Users we are NOT designing for in the MVP

- Individual developers (this is not a developer productivity tool)
- Executives (no executive summary dashboard in MVP)
- HR / Compliance (no employee evaluation features)
- Non-software project managers (construction, manufacturing, etc.)

---

# 4. Design Principles

These principles override any individual feature decision. When in doubt, apply these.

### 1. Project-level analysis, never employee surveillance

The system evaluates project conditions — blocked work, dependency failures, scope changes, quality trends. It never scores, ranks, or evaluates individual employee productivity, commitment, or performance.

The system says: *"The API milestone has increasing delivery risk because three tasks are blocked."*

The system never says: *"Developer X is underperforming."*

### 2. Evidence before explanation

The AI generates an explanation only after structured signals have been detected and supporting evidence has been retrieved from project data. The system never invents reasons without evidence.

### 3. Human authority

The system detects, investigates, and recommends. The human approves, modifies, or dismisses. No consequential action is taken without explicit human approval.

### 4. Cheap computation first, expensive AI second

Routine event processing uses deterministic rules and analytical scoring. The LLM is invoked only when a material or ambiguous risk needs investigation. This keeps the system fast, cheap, and environmentally responsible.

### 5. Data quality is a product feature

The system explicitly reports what data is missing, stale, or unreliable. It does not pretend to have complete information. If data quality is too low for reliable analysis, the system says so rather than producing unreliable alerts.

### 6. Actionability over novelty

The system's value is measured by whether the PM changed what they did — not by how many alerts it produced or how sophisticated the AI is.

---

# 5. MVP Scope

## What the MVP includes

The MVP must deliver a complete, working **risk-to-action loop**:

> Detect → Investigate → Explain → Recommend → Human decides → Act → Track outcome → Learn

### MVP Features

#### F-01: Project onboarding

The PM can create a project and connect data sources.

- Create a project with name, type, description.
- Connect a GitHub repository (issues, milestones, PRs, dependencies).
- Upload a CSV budget file (monthly planned vs actual spend).
- View connection status and data coverage summary.
- View data quality score with identified gaps.

#### F-02: Continuous monitoring

The system periodically syncs project data and evaluates risk signals.

- Automatic periodic sync from connected sources.
- Manual sync trigger.
- Sync history with status and item counts.

#### F-03: Risk signal detection

The system detects risk signals across seven categories using deterministic rules and analytics — no LLM required for detection.

**Categories and example signals:**

| Category | Signals |
|---|---|
| Schedule | Overdue tasks, milestone slippage, increasing cycle time, aging work, declining completion rate |
| Dependencies | Blocked tasks exceeding threshold, overdue upstream dependencies, dependency concentration, handoff delays |
| Scope | New work entering active cycles, requirement churn, priority changes, reopened work |
| Capacity | Demand exceeding capacity, excessive WIP, workload concentration, single-owner bottlenecks |
| Quality | Defect growth, reopened issues, failed builds, increasing test failures |
| Budget | Actual vs planned variance, burn-rate acceleration, forecast variance |
| Decision latency | Overdue approvals, unresolved decisions, long-running blockers |

#### F-04: Risk scoring

Each detected material risk receives:

- Severity: Low / Medium / High / Critical
- Confidence: Low / Medium / High
- Affected project component (milestone, work item group)
- Status: new / active / mitigated / resolved / closed
- Composite score based on configurable category weights

The system does not present scores as statistically calibrated probabilities.

#### F-05: Configurable thresholds

The PM can configure monitoring sensitivity.

- Choose which risk categories to monitor.
- Set thresholds per signal type (e.g., blocked-task warning: 3 days).
- Accept system-recommended defaults or override them.
- Restore defaults at any time.

#### F-06: AI investigation

When a risk crosses a material significance threshold, the AI agent investigates.

The agent:

1. Assembles relevant project context (tasks, dependencies, milestones, defects, history).
2. Retrieves supporting evidence from project records.
3. Identifies likely contributing factors.
4. Explains the risk in human-readable language.
5. Identifies affected milestones and work items.
6. Generates 2–4 practical mitigation recommendations.

Each recommendation includes: action description, rationale, suggested owner, suggested urgency.

Every claim in the explanation must be grounded in retrieved evidence.

#### F-07: Evidence display

Every material risk alert shows the supporting evidence:

- Specific project records (task IDs, dependency links, dates).
- Signal values and thresholds crossed.
- Contributing factors with references.
- The system never presents a risk without showing why it was detected.

#### F-08: Human approval

For each risk and its recommendations, the PM can:

- **Approve** — accept the recommendation as-is, create an action.
- **Modify** — change the recommendation (owner, action, due date), then approve.
- **Dismiss** — reject the risk or recommendation with a required reason.
- **Snooze** — temporarily suppress the alert for a specified duration.
- **Comment** — add context to any risk or recommendation.

#### F-09: Action tracking

Approved recommendations become tracked actions.

Each action has: description, owner, due date, status (pending / in progress / completed / overdue), source risk reference.

The PM can update action status and mark actions complete.

Overdue actions are surfaced in the dashboard.

#### F-10: Outcome tracking and feedback

At milestone completion or risk resolution, the system prompts for outcome feedback:

- Did the intervention help? (Yes / Partially / No / Not sure)
- Optional comment.

For every alert, the PM can provide signal feedback:

- Relevant / Not relevant / Already known / Incorrect / Actionable / Not actionable

This feedback is stored for future system improvement.

#### F-11: Audit trail

The system records the complete decision chain for every risk:

- Risk detected (when, what signals, what severity)
- Evidence used
- Agent explanation and recommendations
- Human decision (approve / modify / dismiss / snooze)
- Actions created
- Outcome recorded

#### F-12: Project health dashboard

The dashboard answers one question within seconds:

> "What requires my attention today?"

Dashboard sections:

1. **Overall project health** — color-coded indicator (green / yellow / orange / red).
2. **Top emerging risks** — sorted by severity, each with a summary and primary recommended action.
3. **Affected milestones** — milestones at risk with health indicators.
4. **Dependency bottlenecks** — blocked items and what is blocking them.
5. **Overdue actions** — approved actions past their due date.
6. **Recent risk changes** — risks that changed severity since last view.
7. **Data quality** — current quality score and identified gaps.

#### F-13: Risk detail page

Accessed by clicking any risk card. Displays:

1. Risk header: severity, category, confidence, status, detected date.
2. Potential impact: affected milestones and work items.
3. Evidence: supporting signals with source references.
4. Contributing factors: ranked root-cause list from the AI agent.
5. Agent explanation: the AI-generated narrative.
6. Risk timeline: severity changes over time.
7. Recommendations: with approve / modify / dismiss controls.
8. Action history: past actions taken for this risk.
9. Outcome: feedback recorded after resolution.

#### F-14: Weekly risk summary

A summary view showing:

- New risks this week.
- Resolved risks this week.
- Risk counts by severity.
- Early warnings surfaced.
- Actions completed vs overdue.
- Comparison with previous week.

---

## What the MVP explicitly excludes

These items are intentionally deferred. They are not scope for the MVP under any circumstances.

| Excluded Feature | Reason |
|---|---|
| Autonomous resource reallocation | Requires trust infrastructure not available in MVP |
| Automatic deadline or budget changes | Too high-risk without established trust |
| Employee performance scoring | Violates Design Principle 1 |
| Individual productivity tracking | Violates Design Principle 1 |
| Private communication analysis | Violates Design Principle 1 |
| Predictive ML models | Requires historical outcome data that does not exist yet |
| Portfolio / cross-project risk | Requires multi-project infrastructure |
| Enterprise SSO / RBAC | Enterprise-tier feature, not MVP |
| Custom model training | Unnecessary complexity for MVP |
| Multi-agent swarms | Single orchestrated workflow is sufficient |
| Dozens of integrations | Start with GitHub + CSV only |
| Real-time event streaming | Periodic sync is sufficient for MVP |
| Kubernetes deployment | Docker Compose is sufficient for MVP |
| Mobile app | Web-only in MVP |
| Email / Slack notifications | Dashboard-only in MVP |
| Executive summary dashboard | Secondary user; defer |
| Non-software project types | Software projects only in MVP |

---

# 6. User Stories

## Onboarding

**US-01:** As a PM, I want to create a new project and connect my GitHub repo so that the system can monitor my project data.

**US-02:** As a PM, I want to upload a CSV budget file so that budget risk signals can be monitored.

**US-03:** As a PM, I want to see what data the system has about my project and what is missing, so I know how reliable the monitoring will be.

## Monitoring

**US-04:** As a PM, I want the system to automatically sync my project data periodically so I don't have to remember to update it.

**US-05:** As a PM, I want to configure which risk categories to monitor and set my own thresholds, so alerts match my project's priorities.

**US-06:** As a PM, I want the system to detect risk signals using rules and analytics, without waiting for an AI model, so detection is fast and reliable.

## Risk Investigation

**US-07:** As a PM, I want the system to investigate material risks and explain why they are emerging, so I understand the root cause without spending hours investigating manually.

**US-08:** As a PM, I want every risk alert to show the specific evidence that triggered it, so I can verify the alert is legitimate.

**US-09:** As a PM, I want the system to recommend 2–4 specific mitigation actions per risk, so I know what to do about it.

## Decision & Action

**US-10:** As a PM, I want to approve, modify, or dismiss each recommendation, so I remain in control of all project decisions.

**US-11:** As a PM, I want approved recommendations to become tracked actions with an owner and due date, so nothing falls through the cracks.

**US-12:** As a PM, I want to see overdue actions highlighted on my dashboard, so I can follow up.

## Outcome & Learning

**US-13:** As a PM, I want to record whether an intervention actually helped, so the system can improve over time.

**US-14:** As a PM, I want to rate each alert as relevant or irrelevant, so the system can reduce false positives.

## Dashboard

**US-15:** As a PM, I want to open the dashboard and immediately see what requires my attention today, without clicking through multiple screens.

**US-16:** As a PM, I want to click on any risk and see the full investigation — evidence, root cause, recommendations, and action history — on one page.

**US-17:** As a PM, I want a weekly summary view that shows how risks changed this week compared to last week, so I can prepare for my review meeting in minutes instead of hours.

## Trust & Transparency

**US-18:** As a PM, I want to see a complete audit trail of every risk detected, every recommendation made, and every decision I took, so I have a defensible record.

**US-19:** As a PM, I want the system to clearly tell me when data is insufficient for reliable analysis, so I don't act on unreliable alerts.

---

# 7. MVP Acceptance Criteria

The MVP is considered functionally complete when a new PM can perform the following journey without developer assistance:

### Starting state

No project is configured in the system.

### End state

The PM has:

1. ✅ Created a project.
2. ✅ Connected a GitHub repository.
3. ✅ Uploaded a CSV budget file.
4. ✅ Viewed the data quality score and understood what data is available.
5. ✅ Configured monitoring thresholds (or accepted defaults).
6. ✅ Viewed the project health dashboard.
7. ✅ Received at least one risk alert with evidence and recommendations.
8. ✅ Opened the risk detail page and understood why it was flagged.
9. ✅ Approved or modified a recommendation.
10. ✅ Seen the recommendation become a tracked action.
11. ✅ Marked an action as complete.
12. ✅ Recorded outcome feedback.
13. ✅ Submitted alert-level feedback (relevant / not relevant).
14. ✅ Viewed the weekly risk summary.
15. ✅ Viewed the audit trail.

If any step requires developer intervention, the MVP is not complete.

---

# 8. Non-Functional Requirements

## Performance

| Requirement | Target |
|---|---|
| Dashboard load time | < 3 seconds |
| Risk engine evaluation (500 work items) | < 5 seconds |
| Data sync (500 work items) | < 30 seconds |
| Agent investigation | < 60 seconds |

## Reliability

- The monitoring pipeline must tolerate: API failures, partial data, duplicate events, delayed updates.
- Sync failures must be logged and retried, not silently dropped.
- The system must function without the LLM (risk detection works; agent investigation is unavailable but the system does not crash).

## Security

- All credentials stored in environment variables, never in code.
- API tokens encrypted at rest in the database.
- All API endpoints validate input.
- Docker containers run as non-root.
- No employee-level personal data stored or sent to LLM prompts.

## Privacy

- Collect only project-level data necessary for risk detection.
- Never collect: private messages, browsing activity, keystrokes, personal communications.
- The system explicitly states it evaluates project conditions, not employees.

## Explainability

- Every risk alert must be traceable: risk → signals → evidence → explanation → recommendation.
- No "black box" scores without supporting evidence.

## Maintainability

- Connectors are modular: adding a new data source does not require modifying the risk engine.
- Risk rules are modular: adding a new rule does not require modifying the connector layer.
- Agent prompts are stored as templates, not hardcoded in logic.

---

# 9. Success Metrics

## Primary success question

> Does the system identify a meaningful risk early enough, explain it clearly enough, and recommend something useful enough that a project manager changes what they do?

## Quantitative targets (pilot validation)

| Metric | Target | How measured |
|---|---|---|
| Alert relevance | ≥ 70% of alerts judged relevant by PM | PM feedback per alert |
| Recommendation actionability | ≥ 60% of recommendations judged actionable | PM feedback per recommendation |
| Critical-risk false positives | < 30% | Dismissed critical alerts ÷ total critical alerts |
| Manager action rate | ≥ 60% of recommendations result in action | Approved ÷ total recommendations |
| Investigation time reduction | ≥ 50% reduction vs manual process | PM self-report: time before vs after |
| Data freshness | > 90% of syncs complete within defined interval | Sync job logs |
| Risk-action traceability | > 90% of risks have a recorded decision | Audit trail completeness |
| User usefulness rating | ≥ 4 / 5 | PM survey |

## Qualitative success criterion

At least one PM should be able to say, in effect:

> "This surfaced something I would not have noticed early enough."

That single statement validates the core product hypothesis.

---

# 10. Data Sources — MVP

| Source | Data Extracted | Method |
|---|---|---|
| **GitHub** | Issues (→ work items), milestones, pull requests (review status, CI status, merge time), cross-references (→ dependencies), labels, assignees | GitHub REST API with incremental sync |
| **CSV file** | Monthly budget: planned vs actual spend per category | File upload via API |

### Data not collected in MVP

- Slack / Teams messages
- Email
- Jira (future connector)
- Confluence / Notion documents (future connector)
- Time tracking systems
- HR / payroll systems

---

# 11. Glossary

| Term | Definition |
|---|---|
| **Risk signal** | A measurable indicator that a project condition may be deteriorating (e.g., "3 tasks blocked > 5 days"). |
| **Risk event** | A detected situation where one or more signals cross configured thresholds and indicate a material risk. |
| **Material risk** | A risk event significant enough to warrant AI investigation and PM attention. |
| **Risk propensity score** | A configurable, weighted composite score indicating how strongly signals suggest risk. Not a statistical probability. |
| **Evidence** | Specific project records (task IDs, dates, dependency links, metrics) that support a risk signal. |
| **Contributing factor** | A likely cause of the risk, identified by the AI agent based on evidence. |
| **Recommendation** | A specific mitigation action proposed by the AI agent for human approval. |
| **Action** | An approved recommendation that has been assigned an owner and due date for tracking. |
| **Outcome** | The recorded result and PM feedback after a risk intervention. |
| **Connector** | A modular integration component that fetches data from one external source and normalizes it. |
| **Signal engine** | The deterministic rules and analytics layer that detects risk signals without using an LLM. |
| **Agent** | The AI reasoning layer (LangGraph workflow) that investigates material risks, retrieves evidence, and generates recommendations. |

---

# 12. Document Governance

This PRD is the authoritative source for what the MVP includes and excludes.

**Any feature not listed in Section 5 "MVP Features" is out of scope.**

If a feature is listed in Section 5 "What the MVP explicitly excludes," it must not be implemented regardless of how easy it appears.

Changes to MVP scope require updating this document first, before writing any code.

---

# Revision History

| Date | Change | Author |
|---|---|---|
| 2026-09-30 | Initial PRD created | Developer |
