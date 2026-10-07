# Tasks: Agentic Content Creator and Scheduler

Source: [plan.md](plan.md). This backlog now targets a production release for one creator, with senior backend, applied AI, and agent engineering evidence. Existing T001–T015 IDs and checkboxes are preserved; T016–T027 add release requirements.

The first functional milestone is an agent that uses tools to create and revise a content plan. The complete MVP adds approval, scheduling, and publication on one real platform.

Paths are proposed except where implementation is explicitly recorded. Short design artifacts are now required where they expose invariants, failure boundaries, or deployment decisions. Follow the dependency order at the end, not numerical ID order.

Current evidence: T002 is in progress. `creator/main.py` provides `/` and `/health`; its Jinja2 template and `config/settings.py` exist. Earlier smoke checks passed for rendering, health, and configuration validation. PostgreSQL connectivity, migrations, reproducible checks, and the mentor understanding review remain outstanding. T001's existing completion records initial choices, not verified account access; T016 must close that gap.

Priority: P0 = required for a safe production release; P1 = required product experience/quality. Both are release requirements. Optional experiments are explicitly separated below. A checkbox means acceptance evidence exists and the learning review is complete; implementation alone does not establish mastery or production readiness.

## How to use the learning sections

Follow the mentor workflow in `AGENTS.md`: resources and explanation first, one small exercise at a time, then implementation and review. Each task below can span several exercises. Direct implementation is allowed when explicitly requested. Read the named sections and apply them to the task artifact; avoid treating every linked resource as a whole course.

Each task includes scope, dependency/priority, acceptance criteria, evidence, and a reasoning question. Run relevant tests as each feature is built; T014 consolidates regression coverage rather than postponing testing. Record implementation evidence and demonstrated understanding separately. Prefer real PostgreSQL for concurrency semantics and fakes for remote side effects.

Original links were checked on 2026-09-23; FastAPI and SQLAlchemy resources replace the Django learning references for the revised stack. Match documentation to installed versions and verify the relevant resource before each lesson. New evaluation, prompt-injection, SLO and backup entry pages were checked for this revision; other resource links are starting points to check when used. LangGraph illustrates concepts, not a framework requirement. The agent-pattern article is foundational reading from 2024; use current provider documentation for implementation details. LinkedIn access requirements are recorded in the plan.

## Phase 1 — Minimal setup

- [x] T001 Confirm the first platform, model provider, and proposed stack in `specs/001-agentic-content-mvp/plan.md`. Check that the intended account can publish text using the platform's official developer tooling. Record any access blocker; simulated publishing can support early work while access is pending.

**Priority/dependencies:** P0; none. Historical decision task; do not infer verified access from its checkbox.
**Senior evidence/review:** Explain provider and platform trade-offs in the plan, identify model-controlled choices versus deterministic authorization, and carry unresolved access/budget decisions into T016. No live post is authorized by a planning decision.

### Learning for T001

**Learn:** The difference between a fixed LLM workflow and an agent that chooses tools, plus the cost of added autonomy.

**In this MVP:** Decide what the model should choose—content angles, needed context, and revisions—and what application code should enforce, such as approval.

**Resource:** [Building effective agents — Anthropic](https://www.anthropic.com/engineering/building-effective-agents). Read “What are agents?” and “When (and when not) to use agents”; use them to write a short explanation of why tool selection helps this product. For platform eligibility, use the selected platform's official developer documentation after it is chosen.

**Understanding check:** Which two decisions benefit from an agent, and which two should never depend on the model's judgment?

- [ ] T002 Create the minimal Python/FastAPI project in `pyproject.toml`, `config/`, and `creator/`, with the app entry point in `creator/main.py`, PostgreSQL configuration in `.env.example`, SQLAlchemy async session setup, Alembic migration configuration, and a basic Jinja2 page in `creator/templates/creator/home.html`. Done when the app runs locally, configuration keeps secrets outside source control, the database connection works, and the creator can open the initial interface.

**Priority/dependencies:** P0; T001. In progress; finish in small mentor-led steps.
**Engineering acceptance:** Reproducible dependency lock, environment validation with no credentials committed, async engine lifecycle and cleanup, one session per request/task, migrations on an empty database, and documented local startup. Separate liveness from database readiness; a database outage must not be reported as ready. Avoid blocking I/O in async handlers.
**Evidence/review:** Save runnable smoke checks for homepage, configuration failure, readiness success/failure, and migration command output. Explain the request lifecycle and connection-pool lifetime. Local setup does not establish production readiness.

### Learning for T002

**Learn:** FastAPI applications and routers, how a request reaches a handler, and when async I/O yields control to other requests.

**In this MVP:** Start with a small web shell that can later accept a content brief. Keep infrastructure work proportionate to that first interaction.

**Resources:** [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/) and [templates](https://fastapi.tiangolo.com/advanced/templates/) — create the app and creator's landing page. Read [async guidance](https://fastapi.tiangolo.com/async/) to distinguish awaitable I/O from blocking calls.

**Understanding check:** What runs when the creator opens the page, and where will agent execution begin later?


## Phase 2 — US1: Create content through an agent

**Outcome:** the creator submits notes and gets a content plan produced through real tool use.

- [ ] T003 [US1] Add creator preferences and source-note input in `creator/preferences.py`, `creator/content.py`, and `creator/templates/creator/brief.html`. Support audience, tone, timezone, preferred posting windows, and one to three requested posts. Done when those inputs can be saved and supplied to the agent across sessions.

**Priority/dependencies:** P1; T002, T017.
**Engineering acceptance:** Bound input length and post count, validate timezone/preferences, retain source IDs and versions, and escape untrusted text when rendering. Associate saved records with the server-selected creator. Draft a stable error contract and test invalid/oversized input and persistence. Local fixtures may supply identity until T018; shared access requires T018.
**Evidence/review:** Validation and PostgreSQL persistence tests; one brief with a minimal context selection rationale. Explain how source edits affect an existing run.

### Learning for T003

**Learn:** Input validation and context selection: collecting information is different from deciding what the model needs for a particular request.

**In this MVP:** Give the agent a focused brief with relevant voice preferences and source notes. Avoid filling every request with unrelated history.

**Resources:** [FastAPI form models](https://fastapi.tiangolo.com/tutorial/request-form-models/) — use Pydantic validation to handle incomplete creator input. [Effective context engineering — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — focus on selecting useful context; use it to prepare a small example brief.

**Understanding check:** What context is necessary for writing a post in the creator's voice, and what can be left out?

- [ ] T004 [US1] Build the agent's context and drafting tools in `creator/agent/tools.py`: read preferences, read source notes, inspect local content/schedule, validate content, save a draft, and propose a time. Use an empty or simulated schedule initially. Done when tool inputs are validated, results are structured, and the tools cannot approve or publish content.

**Priority/dependencies:** P0; T003, T017, T019.
**Engineering acceptance:** Version tool schemas; enforce an allowlist, argument/ownership checks, result-size limits and structured errors. Draft writes use application-generated operation IDs so replay cannot duplicate mutations. The model receives references, never credentials or arbitrary database/file/network execution. Approval/publishing are unavailable tools.
**Evidence/review:** Contract tests for invalid arguments, invented IDs, cross-owner access, timeout and replay; trace one valid call end to end. Prompt-injection resistance is additionally exercised in T020.

### Learning for T004

**Learn:** Tool descriptions, argument schemas, validation, execution, and returning observations to the model.

**In this MVP:** A tool such as reading source notes gives the model information it can act on. A proposed tool call is still input that your application must check.

**Resource:** [Function calling — OpenAI documentation](https://developers.openai.com/api/docs/guides/function-calling). Study the tool-call round trip and input schema. Trace one call to read preferences, including an invalid-input case and application-side authorization.

**Understanding check:** Which component executes the tool, and why does valid JSON not prove the operation is allowed?

- [ ] T005 [US1] Build one tool-calling agent in `creator/agent/runtime.py` and connect the selected model in `creator/agent/model.py`. Let the model select tools, inspect results, write distinct posts, and ask for missing information. Bound tool calls, revisions, runtime, and usage. Done when a real model run demonstrates tool selection and returns grounded drafts with suggested times; a fixed prompt pipeline alone does not complete this task.

**Priority/dependencies:** P0; T004, T019.
**Engineering acceptance:** Version prompt/tool/model configuration; validate tool calls and final output. Implement explicit completion, clarification, failure, cancellation and budget-exhaustion states. Bound tokens, calls, retries, elapsed time and concurrent runs, including across resumes. Apply deadlines and bounded backoff to transient provider failures; account for retries in usage. Never retry mutations blindly.
**Evidence/review:** A real-model trace plus fake-provider tests for malformed output, repeated calls, refusals, rate limits, timeout and exhausted budget. Record token usage, estimated cost with pricing date, and latency. A fake proves control flow, not model quality.

### Learning for T005

**Learn:** The agent loop: model decision → tool call → observation → next decision, with explicit stopping conditions.

**In this MVP:** The agent can discover that it lacks a fact, read another source, or ask the creator before drafting. A fixed sequence of prompts does not demonstrate this decision-making.

**Resources:** [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — read “Agents” and sketch a run. [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling) — follow how tool results return to the next model turn. Add a budget-exhausted ending to your sketch.

**Understanding check:** How does your loop distinguish a finished answer, another tool call, a clarification request, and an exhausted budget?

- [ ] T006 [US1] Connect generation and progress display in `creator/generation.py` and `creator/templates/creator/plan.html`. Run generation as background work, save progress, and present drafts, times, and clarification requests. Done when the creator can complete a brief-to-plan flow and recover saved work after interruption without resetting run limits.

**Priority/dependencies:** P0; T005, T017.
**Engineering acceptance:** Commit job creation durably; workers claim work atomically with recoverable leases. Checkpoints include run versions, tool-operation IDs and consumed budget. Submission retries cannot start duplicate jobs. Restart/cancellation must prevent stale workers from committing new results. Bound queue size and show queued/running/waiting/failed states.
**Evidence/review:** Kill a worker around a draft write, recover the same run, and verify a single draft and preserved budget. Demonstrate browser reconnection and duplicate submission with two worker processes.

### Learning for T006

**Learn:** Background execution, saved checkpoints, and the difference between remembering a result and replaying an action.

**In this MVP:** Closing a browser or restarting a worker should not discard useful drafts or create duplicates when generation resumes.

**Resource:** [Persistence — LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/persistence). Read the checkpoint/thread concepts as a reference design; LangGraph is optional. Draw where your own run saves progress and what it does after an interruption.

**Understanding check:** If a draft was saved just before a crash, how will resuming avoid saving a second copy?


**Review checkpoint:** demonstrate tool calls, resulting drafts, one clarification case, and one stopped run. No real social connection is required for this milestone.

## Phase 3 — US2: Refine and approve the plan

**Outcome:** the creator improves the output conversationally and authorizes exactly what will be published.

- [ ] T007 [US2] Add feedback-driven revision in `creator/agent/revision.py` and `creator/templates/creator/plan.html`. Support requests such as “shorten the second post” or “move the third to Thursday.” Done when the agent changes the intended item, preserves the other posts, and shows the updated text/time for review.

**Priority/dependencies:** P1; T006.
**Engineering acceptance:** Target stable post IDs and expected versions, validate each proposed patch, retain provenance and an audit of changes. Concurrent stale revisions return a conflict. Preserve unaffected posts; distinguish contradictory feedback and missing facts from valid edits. Any material edit invalidates its approval.
**Evidence/review:** Before/after examples and tests for wrong-target edits, stale versions, factual drift and repeated revision requests; explain the stopping rule.

### Learning for T007

**Learn:** Feedback loops, critique criteria, and targeted revision.

**In this MVP:** “Shorten the second post” should change the intended draft while preserving its facts and leaving the other posts intact. Critique is useful only when it improves a defined quality dimension.

**Resource:** [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents). Read “Evaluator-optimizer”; apply the pattern to one before/after revision and assess whether it follows the feedback. This does not require a separate reviewer agent.

**Understanding check:** How will you distinguish a useful revision from a different draft that ignores the creator's request?

- [ ] T008 [US2] Add per-post approve/reject behavior in `creator/review.py` and `creator/templates/creator/plan.html`. Approval must identify the exact content, account, and publication time. Done when edited content or times need fresh approval, repeated approval does not duplicate scheduled work, and rejected items cannot publish.

**Priority/dependencies:** P0; T007, T017, T018.
**Engineering acceptance:** Bind approval to immutable content version, destination and exact publication instant. Enforce authorization and CSRF protection. Approval and durable publication intent commit atomically; database constraints prevent duplicates. Stale approvals conflict, and rejection/revocation transitions are audited.
**Evidence/review:** Real PostgreSQL concurrent edit/approve and repeated-approve tests, unauthorized/forged requests, and transaction rollback. Defend the consistency boundary.

### Learning for T008

**Learn:** Human review checkpoints and atomic changes—related state changes that either succeed together or do not take effect.

**In this MVP:** Approval applies to the actual content, destination, and time shown to the creator. It must not authorize a later edit or create duplicate scheduled work.

**Resources:** [Interrupts — LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/interrupts) — study pause/resume and human review as concepts, without adopting the framework by default. [SQLAlchemy async sessions](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) — study transaction boundaries with `AsyncSession.begin()` and rollback behavior; use them to reason about approving and scheduling together. Give each concurrent task its own session.

**Understanding check:** What happens if the creator edits the post in one browser tab while approving an older version in another?


**Review checkpoint:** revise one of three drafts, reject another, and approve the remaining plan. Demonstrate that an earlier approval cannot authorize a later edit.

## Phase 4 — US3: Schedule and publish

**Outcome:** approved posts publish automatically through our service, with understandable status.

- [ ] T009 [US3] Add durable scheduling in `creator/scheduling.py`. Store approved publication work and resolve the creator's local times into exact publication times. Done when schedules survive restart, future posts do not run early, ambiguous or past times are handled clearly, and overdue behavior is explicit.

**Priority/dependencies:** P0; T008.
**Engineering acceptance:** Persist UTC instants plus original timezone/intent. Explicitly handle nonexistent and repeated local times, past times, overdue jobs and clock differences. Use an indexed due-work query and a documented maximum acceptable lateness from T016.
**Evidence/review:** DST boundary tests, restart/overdue scenarios, and an EXPLAIN plan on representative scheduled rows. Explain why scheduling alone cannot guarantee exact remote publication time.

### Learning for T009

**Learn:** Named timezones, UTC instants, ambiguous local times, and durable scheduling.

**In this MVP:** “Thursday at 9 AM” needs the creator's timezone and an exact date. The schedule must outlive the process that created it.

**Resource:** [Python zoneinfo](https://docs.python.org/3/library/zoneinfo.html). Read timezone construction and the `fold` example. Work through a normal local time and a repeated daylight-saving time, explaining how the creator's intent becomes a publication instant.

**Understanding check:** Why is a fixed UTC offset insufficient for future schedules, and what should happen when the application restarts after a post became due?

- [ ] T010 [US3] Add the selected social platform connection in `creator/platforms/selected.py` and connection controls in `creator/templates/creator/account.html`. Use official supported authorization and publishing behavior; keep credentials outside the agent's context. Done when the correct publishing identity is verified and expired or disconnected access produces a visible reconnect state. Depends on platform access from T001.

**Priority/dependencies:** P0; T016 platform access, T018.
**Engineering acceptance:** Verify the supported LinkedIn publishing endpoint/version and scope against current official documentation. Bind OAuth state to the initiating session, use supported secure authorization flow, verify the publishing identity, encrypt stored credentials with a separately managed key, and redact logs. Handle revoked/expired tokens and documented platform limits. Do not assume refresh tokens, read access, or remote idempotency exist.
**Evidence/review:** Callback/state/identity tests, reconnect demonstration and a capability table with documentation links and account-specific evidence. A live post requires explicit content/account/time approval.

### Learning for T010

**Learn:** Account authorization, permission scope, token expiry, and the distinction between an application's identity and the creator's publishing identity.

**In this MVP:** A connection must identify the actual account that will receive the posts. The agent needs an account reference, not the account's credentials.

**Resource:** [OAuth 2.0 Security Best Current Practice — RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html). Start with section 2.1 on redirect-based flows and section 2.2 on token replay. This is background if the chosen platform uses OAuth, not a replacement for its official connection/publishing guide; select that guide after T001.

**Understanding check:** How do you know which account is connected, what it permits, and when the creator must reconnect?

- [ ] T011 [US3] Build the publishing worker in `creator/worker.py`, using a simulated platform for development. The worker executes approved, due content without another model call. Done when it rechecks approval before sending, handles concurrent claims and restarts, records publishing results, and leaves uncertain remote outcomes for reconciliation rather than blindly retrying. Verify real publication only for a specifically approved test post.

**Priority/dependencies:** P0; T009; T010 for the real adapter (fixtures can proceed independently).
**Engineering acceptance:** Atomically claim due work and recheck approval/version before sending. Use leases/fencing to reject stale-worker state changes. Retry only known-safe failures with capped backoff; uncertain external writes enter reconciliation. Document that a local lock cannot guarantee exactly-once remote effects. Unsupported remote lookup requires manual resolution. Provide a publishing kill switch.
**Evidence/review:** Two-worker races and injected failures before send, after remote acceptance, and before local result commit. Prove bounded retries and no automatic resend after uncertainty; record one explicitly approved real publication.

### Learning for T011

**Learn:** Idempotency, retries, and uncertainty after a remote write.

**In this MVP:** A timeout may happen after the platform accepted a post. Retrying immediately can publish a duplicate even though the application never saw success.

**Resource:** [Making retries safe with idempotent APIs — AWS Builders' Library](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/). Focus on request identity and late-arriving requests. Draw the failure window between remote acceptance and saving the result; investigate what the selected platform actually supports rather than assuming AWS's mechanisms are available.

**Understanding check:** Which failures are safe to retry, and which require checking the remote outcome first?

- [ ] T012 [US3] Add the schedule/result list and pending cancel/reschedule actions in `creator/templates/creator/schedule.html` and `creator/scheduling.py`. Done when the creator can see upcoming posts and published/failed/uncertain results, confirm revised times, and receive an honest conflict if publication has already begun.

**Priority/dependencies:** P1; T011.
**Engineering acceptance:** Cancellation/rescheduling uses version checks and atomic state transitions; rescheduling requires renewed approval. Display uncertain results honestly, provide pagination and bounded queries, and ensure keyboard-accessible forms, labels and visible errors. Show local date, timezone and publishing identity.
**Evidence/review:** Browser walkthrough plus concurrent cancel/send and stale-reschedule tests. Trace why the creator sees a conflict once sending has begun.

### Learning for T012

**Learn:** State transitions, concurrent actions, and presenting uncertainty honestly.

**In this MVP:** A cancel click can race with publication. The interface should report the real outcome rather than promise cancellation after sending has begun.

**Resource:** [SQLAlchemy transactions](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html). Revisit transaction boundaries, then sketch the cancel-versus-send race. Transactions protect local state; they cannot undo a post already accepted by a social platform.

**Understanding check:** What should the creator see if cancellation arrives after the worker has started sending?


**Review checkpoint:** approve a post, restart the application, and verify publication at the scheduled time. Also demonstrate cancellation, rescheduling, and a visible publishing failure.

## Phase 5 — Validate the complete MVP

- [ ] T013 Evaluate the agent with representative briefs in `evals/briefs.jsonl` and record findings in `docs/evaluation.md`. Include missing facts, conflicting timing preferences, revision requests, and repeated topics. Compare with a single-pass generation baseline; review usefulness, grounding, voice, tool behavior, editing effort, response time, and model cost. Done when weaknesses and operating limits are documented with actual examples.

**Priority/dependencies:** P0; T019, T007, T020.
**Engineering acceptance:** Run the held-out suite against the baseline and agent with repeat trials. Report groundedness, voice, revision targeting, constraint adherence and tool-policy violations separately, including weak slices and sample counts. Evaluate final state as well as transcripts. Calibrate any model judge against human labels; report disagreements and uncertainty. Pin run configuration and dataset versions.
**Evidence/review:** Reproducible report against T019's predeclared thresholds, with failures and cost/latency comparison. A policy violation blocks release regardless of average quality. Document whether the agent's benefit justifies its overhead; if not, improve or defer release rather than waive the requirement.

### Learning for T013

**Learn:** Evaluation cases, grading criteria, execution traces, and comparison with a simpler baseline.

**In this MVP:** Evaluate both the usefulness of the final posts and the agent's behavior while producing them. A fluent post is not enough if it invents facts or ignores timing constraints.

**Resource:** [Demystifying evals for AI agents — Anthropic](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Focus on tasks, trials, graders, and outcomes. Create a small rubric and grade the same brief under the agent and a single-pass baseline; keep tuning examples separate from final evaluation cases.

**Understanding check:** What evidence would show that tool use improves this product enough to justify its extra time and cost?

- [ ] T014 Verify important behavior in `tests/test_agent_flow.py` and `tests/test_publishing_flow.py`: run limits, invalid tool calls, approval after editing, restart recovery, duplicate scheduling, cancellation races, timezone handling, expired credentials, and uncertain publishing responses. Done when the checks pass using fixtures by default; live publishing is never an accidental test side effect.

**Priority/dependencies:** P0; T012, T020, T021; tests are developed throughout preceding tasks.
**Engineering acceptance:** Cover state transitions and failure boundaries with isolated PostgreSQL integration tests, provider contracts, browser flows and deterministic clocks/fakes. Prove defaults cannot call live publishing or incur model spend. Include migration upgrade, worker restart and stale lease tests; keep test data free of real secrets.
**Evidence/review:** Reproducible CI run and a failure matrix linking each important invariant to a check. Explain what still needs real-model/platform validation and why a passing mock suite is insufficient.

### Learning for T014

**Learn:** Fixtures, controlled dependencies, and testing observable failure behavior.

**In this MVP:** Simulate slow models, invalid calls, expired credentials, and lost publishing responses without creating real social posts. Use real database transactions for the concurrency checks rather than mocking away the behavior being tested.

**Resource:** [How to use fixtures — pytest](https://docs.pytest.org/en/stable/how-to/fixtures.html). Read fixture setup, reuse, and cleanup. Apply them to a fake model, a fake publishing service, and an isolated test database, then inject one failure at a time.

**Understanding check:** Which tests prove application control flow, and which claims still require a real-model or real-platform demonstration?

- [ ] T015 Document local setup and operation in `docs/runbook.md`, and record the end-to-end demonstration in `docs/mvp-review.md`. Done when a creator can submit notes, interact with the tool-using agent, approve posts, and verify scheduled publication on the chosen platform. Missing live access keeps the final publishing milestone incomplete.

**Priority/dependencies:** P0; T013, T014, T022–T026.
**Engineering acceptance:** Consolidate setup, operation, alert response, reconciliation, credential rotation, restore and rollback instructions. Record an end-to-end staging demonstration and links to real-model/platform evidence. Separate implemented, measured, accepted and still-unverified claims.
**Evidence/review:** A runnable operator walkthrough, known limitations and release evidence index in docs/mvp-review.md. T027 is the final production release decision; documentation alone cannot complete it.

### Learning for T015

**Learn:** Operational visibility and documenting recovery from real failures.

**In this MVP:** A creator needs to know whether work is queued, running, failed, or published. You need enough evidence to explain delays and recover without duplicating actions.

**Resource:** [Monitoring distributed systems — Google SRE](https://sre.google/sre-book/monitoring-distributed-systems/). Read the four golden signals and adapt them to generation and publishing: request duration, workload, failures, and queue pressure. Use this to choose a few useful signals and write one failure-recovery walkthrough; a full monitoring platform is not required.

**Understanding check:** If a scheduled post is missing, how would you determine whether the problem is the worker, credentials, platform, or an uncertain response?


## Production and engineering tasks


These tasks extend the original backlog. Higher IDs do not imply later execution; the dependency sequence below places design, baseline evaluation and security before their consumers.

- [ ] T016 Define the operating envelope and resolve release prerequisites in `docs/release-targets.md`.

**Priority/dependencies:** P0; T001. Can start alongside the remaining T002 exercises.
**Outcome/scope:** Agree what this single-creator service must support and what it costs to operate. Record hosting candidate, deployment region, data sensitivity/provider retention constraints, account access evidence and monthly spending limit. Define expected requests, simultaneous runs, post volume and source sizes.
**Acceptance/evidence:** Give numeric targets, rationale and measurement windows for request availability, generation p95 latency, publication lateness, queue delay, cost per accepted plan, recovery time (RTO) and acceptable data loss (RPO). Mark provisional targets and unresolved choices explicitly; settle them before tests or deployment that depend on them. Check LinkedIn account eligibility and model API access without publishing; missing access remains a release blocker.
**Learn/resource:** [Implementing SLOs — Google SRE](https://sre.google/workbook/implementing-slos/) — study user-facing indicators and error budgets; write a target and measurement method for a late post.
**Review question:** Which promise can we make about our worker, and which depends on LinkedIn or the model provider?

- [ ] T017 Define domain invariants, state transitions and interface contracts in `docs/architecture.md`.

**Priority/dependencies:** P0; T002. Establish contracts before T003; revisit as features land.
**Outcome/scope:** Define creator, source version, run, draft version, approval, job, attempt and connected account. Draw transitions and transaction boundaries; describe handler/service/tool/worker ownership. Choose the durable job mechanism using a short comparison of PostgreSQL-backed work versus a queue.
**Acceptance/evidence:** A compact relationship/state diagram and HTTP/tool contract examples specify authorization, IDs, idempotency, conflict behavior, pagination and error categories. Identify unique/check/foreign-key constraints and indexes, and map each to its owning implementation task. Review crash windows and concurrency interleavings. T017 completes when contracts are reviewed; dependent feature tasks implement and verify enforcement in PostgreSQL. Demonstrate expand/contract thinking for a future incompatible schema change.
**Learn/resource:** [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) and [transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html) — use them to decide which invariants belong in the database.
**Review question:** Which invalid states remain possible if validation exists only in Python?

- [ ] T018 Protect the creator workspace with authentication, authorization and browser security.

**Priority/dependencies:** P0; T003, T017; required before T008, T010 or any shared/hosted access.
**Outcome/scope:** One authenticated creator, with no public signup or team feature. Select a maintained authentication integration and implement server-side identity/ownership checks on every private handler and tool. Threat-model browser, provider and worker trust boundaries in `docs/security.md`.
**Acceptance/evidence:** Secure session expiry/logout, appropriate cookie flags, CSRF protection for mutations, HTML escaping, restricted CORS/hosts, bounded request bodies and login/generation abuse controls. Tests show anonymous requests, forged owner IDs, expired sessions, cross-site mutations and hostile rendered content cannot access/change private state. Local identity fixtures are disabled in hosted configuration.
**Learn/resource:** [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) and [CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) — map controls to the actual template/form workflow.
**Review question:** Why does connecting a LinkedIn account not automatically authenticate every request to our application?

- [ ] T019 Establish the evaluation dataset, grading rubric and cheap baseline before building the agent loop.

**Priority/dependencies:** P0; T003, T016; precedes T004–T005.
**Outcome/scope:** Create versioned development and held-out cases in `evals/`, a manual/template reference and a single-call model baseline. Include missing facts, unsupported claims, long notes, language/voice variation, timing conflicts and revision scenarios. Define measurable quality gates before tuning.
**Acceptance/evidence:** At least 20 representative cases split by source/topic to reduce leakage, with expected constraints/provenance and split rationale. Reserve final cases from prompt tuning. Record model/prompt/settings, token usage, costs and elapsed times; synthetic/mock results are labeled. Define hard policy gates and human-reviewed quality thresholds. Size is an initial learning suite, not a statistical guarantee; grow it from observed failures.
**Learn/resource:** [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — study tasks, trials and graders; turn three briefs into explicit grading criteria.
**Review question:** How could we appear to improve quality simply by tuning on our test set?

- [ ] T020 Test and enforce agent trust boundaries and adversarial behavior.

**Priority/dependencies:** P0; T004–T006, T018; precedes T013.
**Outcome/scope:** Treat source notes, feedback and tool output as untrusted data. Test instructions embedded in notes, invented tool names/IDs, unauthorized retrieval, secret-exfiltration requests and attempts to publish without approval.
**Acceptance/evidence:** Deterministic authorization and tool allowlists block privileged actions even when the model follows malicious text. Bound context/results and reject unsupported operations; show safe error/clarification behavior. Render generated content safely. Use synthetic secret canaries; confirm neither model requests nor traces leak them. Record residual risks; prompt filters alone are not sufficient evidence.
**Learn/resource:** [OWASP prompt injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) — study tool validation and trust boundaries; build an attack/failure table for this agent.
**Review question:** What still prevents publication if the model completely ignores its system instructions?

- [ ] T021 Add reproducible continuous integration and supply-chain checks.

**Priority/dependencies:** P0; T002. Add early; grow alongside feature tests.
**Outcome/scope:** Configure a project-scoped CI pipeline for locked dependency installation, formatting/lint, type checks, meaningful tests, isolated PostgreSQL and migration checks. Resolve a project-local Git boundary before enabling remote CI; the prior Git root resolved to the user's home directory.
**Acceptance/evidence:** A clean checkout passes without local secrets; failures block the pipeline. Scan secrets/dependencies/images as applicable, pin CI actions by immutable references, use least-privilege CI permissions, and document triage of findings. Pull-request jobs cannot access production secrets or publish. No creating a remote repo, pushing or configuring external secrets without user direction.
**Learn/resource:** [GitHub Actions security](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions) — focus on permissions, third-party actions and untrusted input; apply equivalent controls if another CI provider is selected.
**Review question:** What could a pull request execute, and which credentials would it be able to access?

- [ ] T022 Instrument generation and publishing with useful logs, metrics, traces and alerts.

**Priority/dependencies:** P0; T006, T011, T016; add basic correlation while building those tasks.
**Outcome/scope:** Correlate HTTP request, run, tool call, job and publish attempt. Track API errors/latency, queue age, lease recovery, due-post lateness, provider throttling, tokens/cost, budget stops and uncertain outcomes. Audit approval/revision changes.
**Acceptance/evidence:** Structured, redacted telemetry excludes credentials and raw private content by default. Bound label cardinality; choose retention. Demonstrate one trace across a workflow, an actionable alert for stalled publishing and a linked runbook. Distinguish application errors, provider outages and user cancellation. Alert delivery needs an explicitly configured destination.
**Learn/resource:** [OpenTelemetry concepts](https://opentelemetry.io/docs/concepts/signals/) — map traces, metrics and logs to one delayed post; [Google SRE monitoring](https://sre.google/sre-book/monitoring-distributed-systems/) — select actionable signals.
**Review question:** How do you locate a lost post without logging the creator's private notes?

- [ ] T023 Measure capacity, latency and cost under load; enforce backpressure.

**Priority/dependencies:** P0; T012, T013, T016, T022.
**Outcome/scope:** Load-test the agreed operating envelope and a bounded overload case. Set connection-pool/concurrency limits, queue admission, per-creator quotas and global model spending controls. Profile before optimizing.
**Acceptance/evidence:** Record workload, hardware, duration, p50/p95/p99 latency, errors, throughput, queue growth and recovery. Include slow providers and database pressure; isolate overload from health/readiness paths. Use fakes for high-volume remote work and a budgeted real-model sample for cost/latency. Targets in T016 must pass; show bounded rejection and recovery under overload. Account for retries and revisions in cost per accepted plan.
**Learn/resource:** [Locust documentation](https://docs.locust.io/en/stable/) — define realistic user tasks and interpret latency distributions; apply findings to one measured bottleneck.
**Review question:** Why can increasing async concurrency make both latency and reliability worse?

- [ ] T024 Package and deploy a reproducible staging environment with rollback.

**Priority/dependencies:** P0; T018, T021, T016; worker checks require T011.
**Outcome/scope:** Build a minimal non-root image and separate web/worker processes, environment-injected secrets, managed or explicitly operated PostgreSQL, TLS, health/readiness probes and graceful shutdown. Choose hosting using T016's budget; Kubernetes is not required.
**Acceptance/evidence:** Build excludes .env/secrets; use a least-privilege runtime database role and a separate migration role. Run migrations as a controlled release step. Staging has isolated accounts/secrets, publishing disabled by default and a deliberate test allowlist. Demonstrate deploy, worker drain and rollback to a compatible application version, including schema compatibility. Configuration/runbook is reproducible; buying infrastructure or exposing a deployment requires user direction.
**Learn/resource:** [Docker build best practices](https://docs.docker.com/build/building/best-practices/) and [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/) — apply process, restart and resource-lifetime decisions to web and worker.
**Review question:** What happens to a claimed publication when a deployment terminates its worker?

- [ ] T025 Prove backup, restore and incident recovery.

**Priority/dependencies:** P0; T011, T016, T024.
**Outcome/scope:** Schedule encrypted, access-controlled database backups with retention and failure alerts; define ownership. Restore into an isolated environment and rehearse worker crash, provider outage and database outage.
**Acceptance/evidence:** Measure restored-data age and recovery time against RPO/RTO, verify sample records and migration state, and prove restored scheduled jobs do not immediately resend already published posts. Recovery starts with publishing disabled and reconciles external state before enabling it. Record one drill/postmortem with a concrete improvement. A configured backup without a restore does not pass.
**Learn/resource:** [PostgreSQL backup and restore](https://www.postgresql.org/docs/current/backup.html) — compare dump and continuous archiving against the agreed data-loss budget; execute the selected restore approach.
**Review question:** Why can restoring a correct database backup still cause duplicate social posts?

- [ ] T026 Implement data lifecycle and secret rotation.

**Priority/dependencies:** P0; T010, T018, T022, T024.
**Outcome/scope:** Define and enforce retention/deletion for notes, drafts, run traces, OAuth credentials, audit records and backups. Document data sent to the model provider and its configured retention. Implement disconnect and credential rotation procedures.
**Acceptance/evidence:** Demonstrate deletion with pending-work cancellation, defined treatment of in-flight publishing and already-public posts, log/trace redaction, expiration and key/token rotation without accidental publication. Provider-side deletion/retention limitations are explicit; backups follow a documented expiry policy. Injected environment variables are never printed in deployment diagnostics.
**Learn/resource:** [OWASP secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) — apply least privilege, rotation and lifecycle controls to model and social credentials.
**Review question:** After a creator disconnects, what can still exist in a worker, backup, log or provider?

- [ ] T027 Conduct the production release review and an explicitly approved canary.

**Priority/dependencies:** P0; T015 and every required acceptance gate above.
**Outcome/scope:** Review the evidence index, unresolved risks, operating targets, credentials, operator ownership and rollback path. Select a small live canary and an observation window in advance.
**Acceptance/evidence:** No unresolved critical authorization, duplicate-publication, recovery or secret-handling defects; quality/load gates pass; alerts, restore and rollback drills have evidence. Missing real access prevents release completion. Obtain explicit authorization for deployment and exact canary content/account/time. Observe the canary and verify rollback/kill-switch availability; record the go/no-go decision and limits. A successful canary is evidence for this operating envelope, not proof of general availability.
**Learn/resource:** [Google SRE release engineering](https://sre.google/sre-book/release-engineering/) — apply repeatability and rollout controls to the final checklist.
**Review question:** Which evidence would make you stop this release even if the demo looks perfect?

## Dependencies and delivery

1. Continue T002 one small exercise at a time. Establish operating targets in T016.
2. T017 defines contracts; T003 supplies the first saved brief. Add T021 CI early.
3. T019 establishes baseline/evaluation cases; T004–T006 deliver the first tool-using agent demonstration. This milestone can remain local with fixtures.
4. T018 protects hosted access. T007–T009 deliver revision, approval and durable scheduling.
5. T010 (when account access exists), T011 and T012 deliver real publishing. A fake adapter permits local worker development while access is pending.
6. T020 and T013 validate agent security/quality; T014 consolidates feature regression evidence. T022 instruments the full flow.
7. T023–T026 prove capacity, deployment, recovery and data lifecycle; T015 consolidates operational evidence; T027 gates the production canary.

Dependency edges in each task are authoritative. Baseline evaluation and security are early work, not end-of-project additions. Single-creator scope limits product complexity, not authorization or reliability requirements. No calendar estimates are committed until available hours and infrastructure budget are known.

## System design and engineering depth

T028–T034 are required learning-track work, not extra product features or blockers for the single-creator release. Schedule each after its prerequisites, one small exercise per mentoring session. Existing T001–T027 retain their release criteria. Lab results may reveal a real release defect; fix that under the owning release task. Proposed evidence files below are deliverables to create during the exercises, not existing proof of mastery.

| Learning track | Applied release work | Deeper exercise and evidence |
| --- | --- | --- |
| System design | T016 requirements, service targets and capacity; T017 flows | T034 quantified redesign under changed requirements |
| Software architecture | T017 boundaries, invariants and contracts | T028 module boundaries, dependency direction and change-cost comparison |
| Database engineering | T002 connections/migrations; T003 data model; T008 transactions; T009 indexes; T025 restore | T029 MVCC, isolation, locking, query plans and schema evolution |
| Distributed systems | T006 durable execution; T011 uncertain external writes | T030 delivery semantics, outbox, retries, leases and compensation; T032 replication and consensus |
| APIs and networking | T003 validation; T012 conflicts/pagination; T018 authentication; T024 deployment | T033 HTTP semantics, DNS, TLS, proxies and failure diagnosis |
| Performance and scalability | T023 workload, backpressure, pools and profiling | T031 cache correctness; T032 partitioning; T034 scaling thresholds |
| Security, reliability and operations | T018/T020 threat boundaries; T021 CI; T022 telemetry; T024–T027 release/recovery | Failure cases included in each lab; operational evidence reused rather than duplicated |
| AI and agents | T004–T007 tools/runtime; T019/T013 evaluation; T020 attacks; T023 budgets | Apply architecture, data and distributed-systems reasoning to the agent's state and effects |
| Technical leadership | T015 runbooks; T027 release decision | T028 trade-off review and T034 design defense/revision |

- [ ] T028 Review software architecture through one realistic change.

**Priority/dependencies:** Learning required; T017 and T004. Revisit after T011.
**Outcome/scope:** Explain cohesion, coupling, encapsulation and dependency direction using our handlers, application services, domain rules, repositories and external adapters. Compare a modular monolith with extracting the publishing service; identify when each would be justified. Compare direct functions with useful interfaces instead of adding an abstraction at every layer.
**Acceptance/evidence:** In `docs/learning/architecture-review.md`, draw context/container views and trace one command. Implement or sketch an isolated fake-platform substitution; show which modules change and why. Keep business invariants out of HTTP/provider adapters. Explain transaction ownership, test boundaries and the additional operational/consistency costs of service extraction. A refactor needs a demonstrated problem and regression checks; a reasoned decision to keep the structure counts.
**Resources:** [C4 diagrams](https://c4model.com/diagrams) — use context/container views to explain responsibilities; [Parnas, On the Criteria To Be Used in Decomposing Systems into Modules](https://www.cs.umd.edu/class/spring2003/cmsc838p/Design/criteria.pdf) — optional depth on hiding changeable decisions; verify the paper link before the lesson.
**Review question:** If the model provider changes, which modules should change, and which invariants must stay the same?

- [ ] T029 Run a PostgreSQL correctness and performance lab.

**Priority/dependencies:** Learning required; T003 for schema/query work, T008–T009 for concurrency exercises. Deliver one experiment per session.
**Outcome/scope:** Practice normalized schema design and deliberate denormalization, keys/constraints, relational columns versus JSONB, joins and pagination. Investigate MVCC, isolation anomalies, optimistic versus pessimistic locking, deadlocks, indexes and planner statistics. Connect long transactions to vacuum/bloat and connection-pool exhaustion.
**Acceptance/evidence:** In an isolated database with synthetic records, reproduce an approval race with two sessions, compare two fixes, and explain retry behavior. Capture `EXPLAIN (ANALYZE, BUFFERS)` before/after one justified index, including row counts, data distribution and write/storage cost. Compare offset/keyset pagination under inserts. Rehearse an expand/backfill/contract migration with bounded batches and a concurrent writer. Save reproducible commands and results in `docs/learning/database-lab.md`; never run destructive or write-executing analysis against production.
**Resources:** [PostgreSQL concurrency control](https://www.postgresql.org/docs/current/mvcc.html) — study isolation/locking for the race; [Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html) — compare estimated and actual work; [routine vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html) — optional depth on long-transaction effects. Match docs to the lab server version.
**Review question:** When would an index or a stronger isolation level make this workload worse?

- [ ] T030 Demonstrate distributed work and partial-failure semantics.

**Priority/dependencies:** Learning required; T006 and T011.
**Outcome/scope:** Compare at-most-once and at-least-once delivery, deduplication, ordering, atomic database-backed jobs and a transactional outbox when using an external broker. Study acknowledgments, leases/fencing, poison messages, dead-letter handling, bounded retry/jitter, deadlines, bulkheads and circuit breakers. Distinguish a database transaction from a distributed workflow or compensation.
**Acceptance/evidence:** Use two local workers and a fake platform to reproduce duplicate delivery, lost acknowledgment, stale lease and remote-success/local-timeout windows. Trace commit/publish/ack order for a direct enqueue versus outbox. Show retry amplification and bounded recovery; explain when compensation cannot undo an external effect. Save a failure matrix and executable demonstrations in `docs/learning/distributed-work.md`. Adopt new infrastructure only if the release architecture requires it.
**Resources:** [AWS safe retries](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) — reason about request identity; [transactional outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) — inspect the dual-write window; [RabbitMQ acknowledgments and confirms](https://www.rabbitmq.com/docs/confirms) — optional broker semantics, not a requirement to install RabbitMQ.
**Review question:** Which component could guarantee exactly-once effects, and what cooperation would it need from LinkedIn?

- [ ] T031 Evaluate caching with an explicit freshness contract.

**Priority/dependencies:** Learning required; T012 and T023. Use measured read behavior from the uncached service.
**Outcome/scope:** Compare no cache, cache-aside, write-through and write-behind. Explore TTLs, invalidation, versioned keys, stampedes, negative caching and cache outage behavior; distinguish HTTP/browser caching from an application cache. Consider model-response cache keys including prompt/model/source versions and data ownership.
**Acceptance/evidence:** Pick one read path, state allowable staleness, and compare hit/miss latency and database load on synthetic traffic. Test concurrent update, expiration and cache loss. Approval and pre-send authorization still use authoritative state. Record whether the performance gain justifies complexity in `docs/learning/cache-experiment.md`; a supported no-cache decision passes. Do not install Redis in production merely to finish this exercise.
**Resources:** [Azure cache-aside pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/cache-aside) — identify invalidation races; [HTTP caching, RFC 9111](https://www.rfc-editor.org/rfc/rfc9111) — optional depth on cache controls and validation. Check links before teaching.
**Review question:** What could go wrong if an approval check reads a cached draft version?

- [ ] T032 Explore replication, consistency, consensus and partitioning.

**Priority/dependencies:** Learning required; T029 and T030. Separate consistency/replication from partitioning into different sessions.
**Outcome/scope:** Compare synchronous/asynchronous replication, replica lag, read-your-writes and failover. Analyze consistency/availability during a network partition and the scope of a consensus decision. Study quorum, leader election, split-brain risk and fencing. Compare vertical scaling, read replicas, table partitioning and sharding using workload evidence; distinguish SQL/NoSQL choices from consistency guarantees.
**Acceptance/evidence:** Produce a failure timeline for stale approval reads and leader loss; use a local simulation or isolated replica lab, clearly labeled. Explain why a majority decision does not make an external API write atomic. For a hypothetical larger workload, choose a partition key, identify hot keys, cross-shard operations and a rebalance strategy. Save trade-offs and observable failure outcomes in `docs/learning/replication-and-scale.md`. No production cluster, custom consensus implementation or actual sharding is required.
**Resources:** [PostgreSQL high availability and replication](https://www.postgresql.org/docs/current/high-availability.html) — compare lag/durability choices; [Raft](https://raft.github.io/) — study leader election and log replication using its paper/visualization; [PostgreSQL partitioning](https://www.postgresql.org/docs/current/ddl-partitioning.html) — distinguish table partitioning from distributed sharding.
**Review question:** If the database is unreachable but a worker has an old approval cached, should it publish? Defend the consistency and availability trade-off.

- [ ] T033 Trace a request through networking and API boundaries.

**Priority/dependencies:** Learning required; T002 for local HTTP, T024 for the TLS/proxy trace.
**Outcome/scope:** Trace DNS resolution, connection establishment, TLS, reverse proxy/load balancer and ASGI handling. Compare connect/read/overall deadlines, connection reuse and graceful shutdown. Explain HTTP safety/idempotency, error contracts, conditional updates, API evolution and asynchronous request/reply. Compare polling, SSE and WebSockets for run progress; discuss REST versus RPC/GraphQL only where requirements differ.
**Acceptance/evidence:** Capture sanitized headers/timings and trace one request across the selected deployment. Simulate a DNS/connect failure, proxy timeout and application error; distinguish their symptoms without exposing credentials. Document trusted proxy configuration, TLS termination and health-routing behavior. Record a protocol choice for progress updates and backward-compatible API change in `docs/learning/request-path.md`; no extra protocols need shipping.
**Resources:** [HTTP semantics, RFC 9110](https://httpwg.org/specs/rfc9110.html) — read methods, status codes and intermediaries; [FastAPI behind a proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/) — apply forwarding/trust configuration; [TLS 1.3, RFC 8446](https://www.rfc-editor.org/rfc/rfc8446) — optional handshake overview. Verify relevant sections before the lesson.
**Review question:** Why might the client receive a timeout even though our server has already committed the operation?

- [ ] T034 Defend and evolve the complete system design.

**Priority/dependencies:** Learning required; T028–T033 and measured T023 results. Does not block T027.
**Outcome/scope:** Revisit requirements, non-goals, latency/availability/consistency targets, traffic, bandwidth, storage growth and costs. Use the measured single-creator system as a baseline; model a clearly hypothetical 100x workload and a provider outage. Compare two plausible architectures and identify the next bottleneck before choosing components.
**Acceptance/evidence:** In `docs/learning/system-design-defense.md`, provide capacity calculations with units and assumptions, critical-path diagrams, alternatives, chosen trade-offs and thresholds for revisiting them. Explain data ownership, migration compatibility, failure isolation, observability, privacy and operational cost. Defend a deployment/migration plan against one changed requirement and revise it after mentor review. Compare CQRS/event sourcing, service extraction and managed infrastructure only when they address an identified constraint. Make an explicit keep/defer/reject decision for each proposed addition.
**Resources:** Reuse T016's SLO resource, T028's C4 guide and the measured reports from T023/T029–T033; assign only the relevant section for each review. This is a production-reasoning capstone, not an interview script.
**Review question:** What is the smallest change that meets the new requirement, and what evidence would disprove your design?

## Optional learning experiments — outside release scope

After the baseline identifies a specific weakness, a separately scoped experiment may compare retrieval/reranking for larger note collections, model routing/caching, fine-tuning, or a second specialist agent. Require a hypothesis, held-out comparison, cost/latency budget and a keep/reject decision. Do not add vector databases, multiple agents, Kubernetes or GPU infrastructure simply to claim seniority. This project targets applied AI and agent engineering; it does not replace a full ML-training or research curriculum.

## Review standard

For each task, distinguish “read,” “implemented with assistance,” “verified,” and “can explain and defend.” Record actual evidence in the task's named artifact, not an invented proficiency score. Senior-level progress means reasoning about trade-offs, measuring behavior, recovering from failures and explaining the result. Production readiness remains unverified until T027 passes.
