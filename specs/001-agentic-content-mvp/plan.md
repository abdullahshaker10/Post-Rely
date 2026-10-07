# Plan: Agentic Content Creator and Scheduler

## Main idea

Build our own content creation and scheduling product, inspired by Postiz. A creator gives the agent a goal and source notes. The agent uses tools to understand the context, create posts, improve them, and propose a publishing schedule. After the creator approves, the application publishes the posts automatically.

The agentic workflow is the core of the first MVP. The first working demonstration should already show an agent selecting tools and responding to feedback.

## Product scope and engineering goal

The product remains a small MVP, but the implementation and learning goal now includes system design, software architecture, database engineering, distributed systems, networking/APIs, performance/scalability, senior backend engineering, applied AI engineering, agent design, and production operation. Build in small mentor-led exercises using resources first, as specified in `AGENTS.md`. Demonstrate design judgment, correctness under concurrency/failure, evaluation quality, security, and recovery; adding frameworks alone is not progress.

Start with one creator, one social platform, one connected account, and text-only content. A request can produce up to three posts.

The creator can:

1. Set their audience, writing style, timezone, and posting preferences.
2. Give the agent a topic or source notes.
3. Receive draft posts and suggested publication times.
4. Ask the agent to revise specific posts or change the plan.
5. Approve the content and schedule.
6. See scheduled posts, cancel or reschedule pending ones, and check publishing results.

Example: “Turn these notes into three posts for next week. Keep my tone practical, use weekday mornings, and show me the plan before scheduling.”

## How the agent works

Use one agent that can read the creator's preferences and notes, check existing content and scheduled posts, save drafts, validate content, and propose publication times.

The agent decides which tools it needs, evaluates their results, and continues until it has a useful plan or needs clarification. It revises content based on feedback and has limits on how long it can run.

The creator approves the final content, account, and time. A background worker then publishes the approved posts when due. Scheduling continues even when the agent is no longer running.

## Proposed technologies

| Part | Proposed technology |
| --- | --- |
| Backend | Python with FastAPI and Pydantic validation |
| Interface | Simple Jinja2 templates with lightweight JavaScript |
| Storage | PostgreSQL with SQLAlchemy async sessions and Alembic migrations |
| Agent | One tool-calling language model with a small orchestration loop |
| Background work | A separate worker for generation and scheduled publishing |
| Social connection | Direct integration with the first selected platform |
| Development checks | pytest and local fixtures for model/platform behavior |

### Confirmed T001 decisions

| Decision | Choice | Why |
| --- | --- | --- |
| First social platform | LinkedIn member text posts | It directly supports text-only publishing through the self-service Share on LinkedIn product and fits the initial professional-content use case. |
| Model provider and interface | OpenAI Responses API with function calling | It supports the application-controlled tool-call loop required by this MVP; application code will execute and validate every requested tool call. |
| Initial model candidate | `gpt-5` (previously proposed, not benchmarked) | Keep the model configurable; T016 checks actual access and T019/T013 measure quality, cost and latency before accepting a production model. No claim that this is the current best or cheapest model. |
| Application stack | Python 3.12, FastAPI, Pydantic, PostgreSQL, SQLAlchemy async, Alembic, Jinja2 templates, a separate Python worker, pytest | FastAPI supports concurrent I/O while waiting for model, database, and platform calls; the first release remains a small, server-rendered product. |

No agent framework is required. The runtime will own the tool loop and its limits.

Use async-compatible clients for model, database, and platform I/O. Declaring a handler `async def` does not make blocking calls nonblocking. Each concurrent task owns its database session. Generation and scheduled publishing run in a separate worker with durable database-backed work; FastAPI's in-process `BackgroundTasks` is not the durable scheduler. See [FastAPI async guidance](https://fastapi.tiangolo.com/async/) and [background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/).

### Platform access prerequisite

Before real LinkedIn publishing, create a LinkedIn app, add the **Share on LinkedIn** product, configure an OAuth redirect URI, and connect the test member with the `w_member_social` permission. Actual account eligibility, granted permissions and current supported publishing APIs still require verification in T016/T010. T001's preserved checkbox records the initial selection, not demonstrated access. Worker and UI work may use a simulated platform while access is pending; production release cannot.

## Delivery approach

Establish operating targets, domain invariants and a baseline evaluation before expanding agent autonomy. Build the local agentic experience using supplied context and a simulated platform, then add creator review, durable scheduling and the real platform connection. Add tests with each feature, CI early, and authentication before shared/hosted access. Follow dependencies in tasks.md rather than task ID order.

Success means a creator can go from notes to useful posts, refine them through the agent, approve the schedule, and see the posts published on one platform. Failures should be visible, and restarting the application should not lose scheduled work.

### Milestones and release gates

| Milestone | Required evidence |
| --- | --- |
| Local foundation | T002 setup, database readiness, migrations and request-lifecycle explanation; T016 operating targets and T017 invariants |
| Agent demonstration | T019 baseline and evaluation cases, T003–T006 grounded drafts through real tools, clarification and bounded failure/recovery |
| Controlled publishing | T018 authenticated access, T007–T012 version-bound approval, schedule/cancel races and approved real-platform evidence |
| Quality and operational validation | T013/T014 evaluation and regressions, T020 agent security, T021 CI, T022 telemetry, T023 measured capacity/cost |
| Production release | T024 staging/rollback, T025 restore drill, T026 data/secret lifecycle, T015 runbooks, T027 explicitly authorized canary and evidence review |

Production-ready means verified for the agreed single-creator operating envelope, not unlimited scale or a blanket security guarantee. T016 must establish numeric quality/latency/cost/recovery targets and measurement windows before dependent validation. T019 defines quality thresholds before tuning. Deterministic application controls own authorization, approval and spending limits; the model chooses context tools, content and revisions within those bounds.

Run the web process and durable worker separately. Prefer a simple deployment with PostgreSQL, reproducible images, injected environment variables/secrets and TLS. Hosting provider, budget, region, authentication integration and final durable-job mechanism remain decisions to validate; this planning update does not authorize purchases, external deployment or social posting.

Short architecture/contracts and failure analyses are now part of the tasks. Evidence belongs in the task's named artifact; tasks.md remains the authoritative progress checklist. The current implementation has a homepage, liveness endpoint and settings validation; PostgreSQL, migrations, agent behavior and production infrastructure are not implemented.

## Outside this MVP

The learning coverage matrix and T028–T034 in tasks.md connect these disciplines to the release work and add deeper labs. These are required for the expanded learning path, not additional blockers for the scoped production release. Each lab produces a reviewed artifact or measured experiment; proficiency remains unassessed until demonstrated. Advanced architecture is studied through comparisons and isolated exercises before considering product adoption.

Multiple platforms, images and videos, team accounts, analytics-based recommendations, open-web research, and multiple cooperating agents.

## Documents

- [Product idea](../../docs/agentic-mvp/BRIEF.md)
- [Detailed tasks](tasks.md)

This revision expands engineering and learning scope beyond the initial 15-task demo-oriented checklist. T001–T015 retain their IDs/statuses; T016–T027 add required production work; T028–T034 add the system-design and engineering-depth learning track. Delivery and learning effort increase; no deadline or budget is assumed. Spec Kit is installed, but these documents are a maintained lightweight plan/backlog, not a claim that formal specification or constitution workflows have been completed.
