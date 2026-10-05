# RiskZen — Validated Software Project Risk Taxonomy

**Document version:** 1.0.0  
**Date:** 2026-10-04  
**Status:** Validated  
**Author:** RiskZen Architecture & Research  

---

## 1. Executive Summary & Purpose

Software engineering projects fail predominantly due to predictable, recurring systemic patterns rather than unforeseen "black swan" events (*DeMarco & Lister, 2003*). However, traditional project management dashboards only capture **lagging indicators** (e.g., missed deadlines, exceeded budgets, delivered defect spikes) after damage is already irreversible.

This document establishes the **Validated Risk Taxonomy** for RiskZen. It synthesizes empirical project management literature, Agile software metrics, and the DORA (*DevOps Research and Assessment*) body of knowledge into **8 structured risk categories**, each defined with:
1. Academic and empirical foundation
2. Observable leading indicators (detectable 2–6 weeks before milestone failure)
3. Quantitative telemetry and data source mappings (GitHub API, Git commits, CSV/financial logs)
4. Detection threshold triggers and severity heuristics
5. Recommended algorithmic & AI mitigation actions

---

## 2. Literature Foundations

The taxonomy is grounded in the following canonical software management research:

| Source | Core Insight Applied in RiskZen |
|---|---|
| **Brooks, F. P. (1975)** *The Mythical Man-Month* | *Brooks's Law:* Adding manpower to a late software project makes it later due to communication overhead. *Leading indicator:* Rampant task reassignment and splintered dependencies. |
| **Boehm, B. (1991)** *Software Risk Management: Principles and Practices* | Identifies the top 10 software risks, notably: Personnel shortfalls, unrealistic schedules, gold plating/scope creep, and continuous requirement churn. |
| **McConnell, S. (1996)** *Rapid Development: Taming Wild Software Schedules* | Categorizes schedule risks into "Classic Mistakes" (overly optimistic schedules, developer friction, poor dependency management, feature creep). |
| **DeMarco, T. & Lister, T. (2003)** *Waltzing with Bears: Managing Risk on Software Projects* | Risk management is not about risk elimination; it is about risk mitigation and continuous proactive discovery. |
| **Forsgren, N., Humble, J., & Kim, G. (2018)** *Accelerate / DORA* | Establishes statistical links between Lead Time for Changes, Deployment Frequency, Change Failure Rate, and Mean Time to Restore (MTTR) with delivery predictability. |
| **Little, J. D. C. (1961)** / *Kanban Principles* | *Little's Law:* $L = \lambda W$. Uncontrolled Work-in-Progress (WIP) directly inflates cycle time and introduces delivery variance. |

---

## 3. The 8 Core Risk Categories & Indicator Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                       RISKZEN RISK TAXONOMY                            │
├───────────────────┬───────────────────┬────────────────────────────────┤
│ 1. Schedule Risk  │ 2. Dependency     │ 3. Scope Influx                │
│ Velocity decline, │ Cascading delays, │ Requirement churn,             │
│ Milestone slip    │ Blocked items     │ Gold plating                   │
├───────────────────┼───────────────────┼────────────────────────────────┤
│ 4. Capacity Risk  │ 5. Quality Drag   │ 6. Decision Latency            │
│ Bus factor spike, │ Reopened bugs,    │ Stalled PRs,                   │
│ Excessive WIP     │ Defect density    │ Unresolved architecture RFCs   │
├───────────────────┼───────────────────┼────────────────────────────────┤
│ 7. Budget Burn    │ 8. Stale Cadence  │                                │
│ Variance drift,   │ Dormant initiatives│                               │
│ Cost acceleration │ Inactive issues   │                                │
└───────────────────┴───────────────────┴────────────────────────────────┘
```

---

### Category 1: Schedule Slippage & Velocity Degradation

- **Definition:** The mathematical trajectory of work completion indicates the project will not deliver committed scope by the target milestone date.
- **Literature Basis:** *McConnell (1996)* on "Schedule Creep"; *Agile Velocity Variance Theory*.

#### Indicators & Data Sources

| Indicator Type | Observable Metric | Telemetry Source | Formula / Signal |
|---|---|---|---|
| **Leading** | Historical Velocity Degradation | GitHub Issues / Milestones | Completed story points or issue count in rolling 14-day window $< 75\%$ of 60-day moving average. |
| **Leading** | Remaining Scope vs. Time Horizon | GitHub Milestones | $\text{Projected Completion} = \text{Remaining Open Items} / \text{Current Velocity} > \text{Days Until Due Date}$. |
| **Lagging** | Overdue Task Accumulation | GitHub Issues | Count of open work items where $\text{due\_date} < \text{current\_date}$. |

#### Severity Triggers
- **Low:** Estimated milestone slip between 1–3 business days.
- **Medium:** Estimated milestone slip between 4–7 business days; $>10\%$ of milestone tasks past due.
- **High:** Estimated milestone slip between 8–14 business days; $>25\%$ of milestone tasks past due.
- **Critical:** Estimated milestone slip $> 14$ business days or negative completion trajectory.

---

### Category 2: Dependency Blocking & Cascading Delay

- **Definition:** Critical path work items are stalled awaiting completion of upstream prerequisites, threatening downstream delivery chains.
- **Literature Basis:** *Goldratt, E. (1997)* *Critical Chain Project Management (CCPM)*; *Boehm (1991)* on "External Component Shortfalls".

#### Indicators & Data Sources

| Indicator Type | Observable Metric | Telemetry Source | Formula / Signal |
|---|---|---|---|
| **Leading** | Upstream Item Inactivity | GitHub Issues / PRs | Blocker issue has had 0 commits/comments for $> 5$ consecutive days while downstream items remain open. |
| **Leading** | Deep Dependency Chains | Issue relations / Dependency graph | Dependency depth $\ge 3$ levels on un-started work items. |
| **Lagging** | Blocked Active Items | GitHub Issue Labels / Linked PRs | Items explicitly tagged `blocked` or linked with `blocked by #ID` whose blocker is unresolved. |

#### Severity Triggers
- **Low:** 1 non-critical path task blocked for $< 3$ days.
- **Medium:** 2–3 tasks blocked, or 1 milestone deliverable blocked for $\ge 3$ days.
- **High:** Critical path milestone blocker unresolved for $\ge 5$ days with multiple downstream dependents.
- **Critical:** Cascading blockage affecting $\ge 30\%$ of active sprint deliverables.

---

### Category 3: Scope Creep & Requirement Churn

- **Definition:** Uncontrolled expansion of project deliverables and acceptance criteria without proportional adjustments to schedule, resources, or budget.
- **Literature Basis:** *Boehm (1991)* on "Continuing Stream of Requirements Changes"; *Standish Group Chaos Studies*.

#### Indicators & Data Sources

| Indicator Type | Observable Metric | Telemetry Source | Formula / Signal |
|---|---|---|---|
| **Leading** | Milestone Work-Item Influx | GitHub Milestones | Net new issues added to an in-flight milestone $> 15\%$ after sprint/milestone kickoff date. |
| **Leading** | Requirement Churn Frequency | Issue Descriptions & Edit History | $> 3$ major description edits or label renegotiations on active work items within 7 days. |
| **Lagging** | Unestimated Scope Growth | CSV / Project Metadata | Percentage of total milestone tasks without time/point estimates $> 20\%$. |

#### Severity Triggers
- **Low:** Milestone scope increased by $5\% - 10\%$ post-kickoff.
- **Medium:** Milestone scope increased by $11\% - 20\%$; $> 3$ new unestimated tasks added in mid-cycle.
- **High:** Milestone scope increased by $> 20\%$ without target date recalibration.
- **Critical:** Milestone scope increased by $> 35\%$, causing immediate milestone target infeasibility.

---

### Category 4: Capacity Overload & Single-Point Bottleneck (Bus Factor)

- **Definition:** Asymmetric concentration of critical tasks, reviews, and domain knowledge on a small subset of team members, creating systemic flow bottlenecks and burnout risk.
- **Literature Basis:** *Brooks (1975)*; *Little's Law (1961)*; *Cockburn (2001)* on team velocity dynamics.

#### Indicators & Data Sources

| Indicator Type | Observable Metric | Telemetry Source | Formula / Signal |
|---|---|---|---|
| **Leading** | Workload Asymmetry / Gini Coefficient | GitHub Assignees | $> 40\%$ of all active, high-priority milestone items assigned to a single developer. |
| **Leading** | Excessive Work In Progress (WIP) | GitHub Issues in `in_progress` | Individual developer WIP $> 4$ concurrent active tasks. |
| **Lagging** | PR Review Gate Bottleneck | GitHub Pull Requests | $> 5$ open PRs awaiting review from the same single assignee for $> 72$ hours. |

#### Severity Triggers
- **Low:** Single developer assigned 3 concurrent active tasks; no blocked reviews.
- **Medium:** Single developer assigned $\ge 5$ active tasks; 2–3 PRs pending their review $> 48$h.
- **High:** Single developer holds $> 40\%$ of milestone critical path; PR review queue $> 5$ items.
- **Critical:** Developer bottleneck causing cross-team stall with $> 3$ downstream blocked dependencies.

---

### Category 5: Quality Drag & Defect Accumulation

- **Definition:** High influx and reopening of software defects diverting capacity from planned feature development, resulting in negative forward velocity.
- **Literature Basis:** *Humphrey, W. (1989)* *Managing the Software Process*; *DORA metrics (Change Failure Rate)*.

#### Indicators & Data Sources

| Indicator Type | Observable Metric | Telemetry Source | Formula / Signal |
|---|---|---|---|
| **Leading** | Bug Influx vs. Resolution Ratio | GitHub Issues (`type: bug`) | New bugs filed per week exceeds resolved bugs by $> 25\%$ over 2 consecutive weeks. |
| **Leading** | Bug Reopen Spike | GitHub Issues | $> 15\%$ of closed defect issues reopened within 7 days of closing. |
| **Lagging** | High-Severity Defect Debt | GitHub Issues (`priority: critical/high`) | $\ge 3$ open critical bugs unresolved for $> 5$ business days. |

#### Severity Triggers
- **Low:** Bug count steady; resolution rate matches creation rate.
- **Medium:** Bug creation outpaces resolution by $15\% - 30\%$; 1 critical bug open $> 3$ days.
- **High:** Bug reopening rate $> 20\%$; feature development stalled due to bug firefighting.
- **Critical:** $\ge 3$ critical defects blocking release; zero net feature progress over 14 days.

---

### Category 6: Decision Latency & Governance Stalls

- **Definition:** Prolonged delays in architectural approvals, stakeholder sign-offs, and pull-request code reviews creating invisible delivery latency.
- **Literature Basis:** *Poppendieck, M. & T. (2003)* *Lean Software Development: An Agile Toolkit* on "Eliminating Waste / Waiting Waste".

#### Indicators & Data Sources

| Indicator Type | Observable Metric | Telemetry Source | Formula / Signal |
|---|---|---|---|
| **Leading** | PR Review Dormancy | GitHub Pull Requests | Open PR with zero review activity or unresolved comments for $> 4$ business days. |
| **Leading** | Architecture RFC / Decision Delay | GitHub Issues / Discussions (`label: decision`) | Decision item open with $> 10$ comments but no decision reached for $> 7$ days. |
| **Lagging** | Blocked Task Due to Missing Specs | GitHub Issues | Task status explicitly flagged `waiting-for-decision` for $> 5$ days. |

#### Severity Triggers
- **Low:** 1 PR awaiting review between 48h and 72h.
- **Medium:** 2–3 PRs awaiting review $> 72$h; 1 design decision pending $> 5$ days.
- **High:** Core architectural decision stalled $> 10$ days, blocking multiple sprint tasks.
- **Critical:** Release-blocking PR or governance approval pending $> 14$ days.

---

### Category 7: Budget Burn Rate Discrepancy

- **Definition:** The rate of financial or resource expenditure significantly deviates from the planned earned-value baseline.
- **Literature Basis:** *Project Management Institute (PMI) PMBOK Guide* — *Earned Value Management (EVM)* principles (Cost Variance $CV = EV - AC$, Cost Performance Index $CPI = EV / AC$).

#### Indicators & Data Sources

| Indicator Type | Observable Metric | Telemetry Source | Formula / Signal |
|---|---|---|---|
| **Leading** | Cost Performance Index (CPI) Drift | CSV Financial Ingestion / Time Logs | $CPI < 0.85$ (spending $\$1.00$ to achieve $\$0.85$ of earned value). |
| **Leading** | Resource Consumption vs Milestone % | Financial CSV vs GitHub Milestones | Budget consumed $> 60\%$ while milestone progress $< 40\%$. |
| **Lagging** | Projected Total Overrun | Budget Records | Projected total project cost exceeds baseline allocation by $> 15\%$. |

#### Severity Triggers
- **Low:** $CPI$ between $0.90$ and $0.95$.
- **Medium:** $CPI$ between $0.80$ and $0.89$; projected overrun between $5\% - 15\%$.
- **High:** $CPI < 0.80$; projected overrun $> 15\%$.
- **Critical:** Budget exhausted before reaching final development milestones.

---

### Category 8: Stale Initiatives & Dormant Work

- **Definition:** Work items or sub-projects that remain officially active in trackers but have ceased to show code commits, comments, or movement, disguising stalled commitments.
- **Literature Basis:** *Larman, C. & Vodde, B. (2010)* *Practices for Large-Scale Agile*.

#### Indicators & Data Sources

| Indicator Type | Observable Metric | Telemetry Source | Formula / Signal |
|---|---|---|---|
| **Leading** | Issue Inactivity in In-Progress State | GitHub Issues | Status is `in_progress` with 0 updates/commits for $\ge 10$ business days. |
| **Lagging** | Milestone Target Date Passed | GitHub Milestones | Target date in the past with open items remaining. |

#### Severity Triggers
- **Low:** $1 - 2$ tasks inactive for $10$ days.
- **Medium:** $> 15\%$ of active sprint tasks inactive for $> 10$ days.
- **High:** Key milestone component inactive $> 20$ days without formal deprioritization.
- **Critical:** Abandoned deliverable with unaccounted dependent commitments.

---

## 4. Telemetry Extraction Mapping

| Data Entity | Telemetry Extracted by Connector | Mapped Risk Categories |
|---|---|---|
| **GitHub Issues** | State, Created Date, Updated Date, Due Date, Assignees, Labels, Milestone ID, Body text keywords (`blocked by #...`, `depends on #...`) | Schedule, Dependency, Scope, Capacity, Quality, Stale |
| **GitHub Pull Requests** | State, Created Date, Updated Date, Reviewers, Review Comments, Merge Date, Additions/Deletions | Decision Latency, Capacity, Quality |
| **GitHub Milestones** | Title, Due Date, Open Issues Count, Closed Issues Count, State | Schedule, Scope, Stale |
| **CSV Ingestion** | Category, Budget Allocated, Budget Spent, Billing Period, Resource Rate | Budget Burn Rate |

---

## 5. Algorithmic & AI Agent Action Framework

When a risk pattern is flagged by the deterministic rule engine:
1. **Rule Engine:** Calculates composite risk propensity score $P \in [0.0, 1.0]$.
2. **LangGraph Agent:** Retrieves contextual vector evidence (issue transcripts, PR diff summaries, dependency paths) and generates root-cause analysis.
3. **Mitigation Formulation:** Produces concrete, human-in-the-loop recommendations (e.g., "Reassign Task #42 from Dev A to Dev B", "Split PR #108 into two smaller diffs", "Renegotiate Milestone due date by +4 days").
4. **Audit Trail:** Logs every detection, recommendation, PM decision, and outcome feedback into an immutable PostgreSQL audit ledger.

---

## 6. Document Validation Sign-off

- **Taxonomy completeness:** 8 core software delivery risk dimensions covered.
- **Leading indicator coverage:** 100% of categories include actionable leading signals.
- **Data source feasibility:** All signals map directly to standard GitHub REST API endpoints and CSV schema.
