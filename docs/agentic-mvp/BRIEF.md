# Agentic Content Creator and Scheduler

## The idea

Build an independent content creation and publishing product inspired by Postiz. A creator describes what they want to communicate, supplies source material, and lets an AI agent help turn that intent into a publishing plan.

The product brings content ideation, writing, revision, scheduling, and publishing into one workflow. The creator sets direction and reviews the result; the system carries out the approved plan.

Postiz is a reference for the product experience. This product owns its content workflow and scheduling system and connects directly to social platforms.

## Who it is for

The initial user is an individual creator who has ideas or knowledge to share but spends too much time turning them into consistent posts and managing when they go live.

The broader vision can serve professionals, founders, and small teams who want a consistent publishing presence while retaining control over their voice and content.

## The problem

Content creation involves repeated decisions: what to write, how to express it, whether it fits the audience, when to publish it, and whether it actually went live. These decisions often happen across disconnected writing, planning, and scheduling tools.

The product should let the creator express an outcome and collaborate with an agent through the whole process, with clear visibility into the resulting content and scheduled actions.

## What makes it agentic

The agent works toward a content goal using context and tools. It can read the creator's preferences and source notes, inspect existing drafts and scheduled posts, choose content angles, write drafts, evaluate them, revise them, and propose publication times.

It can ask for missing information and adapt its plan to feedback. For example, a request to make a post more practical should lead it to revise the relevant draft while preserving the rest of the plan.

The backend enforces content validation, approval, and scheduling rules. Once a plan is approved, a persistent scheduler publishes it at the intended time. The agent does not need to stay running or make another creative decision when a post becomes due.

## Example experience

> “Turn these notes into three posts for next week. Write for backend engineers, keep my tone practical, and use weekday mornings in my timezone. Show me the posts and times before scheduling.”

The agent reads the notes and brand preferences, proposes three distinct angles, writes the posts, and suggests times that fit the creator's preferences and existing schedule.

The creator can respond:

> “Make the second post shorter and move the third one to Thursday.”

The agent updates the affected parts of the plan. After the creator approves, the product schedules the posts and displays their publishing status.

## MVP goal

Prove that one creator can move from a content brief to useful, reviewed posts that are automatically published on one social platform at approved times.

The first release includes the complete creation-to-publication workflow, with a deliberately small product scope and a production engineering bar. This is also a mentor-led learning project covering system design, software architecture, databases, distributed systems, networking, scalability, senior backend, applied AI and agent engineering: resources, small exercises, review and evidence accompany each task. Deeper labs and the design capstone extend learning without making advanced infrastructure a release requirement; see the coverage matrix in the [backlog](../../specs/001-agentic-content-mvp/tasks.md).

## MVP scope

| Area | First-release capability |
| --- | --- |
| Creator | One user and one connected social account |
| Platform | LinkedIn member text posts; actual developer/account access remains to be verified |
| Content | Text-only posts, up to three per request |
| Inputs | A brief, pasted text or Markdown notes, audience, voice, timezone, and posting preferences |
| Creation | Content angles and drafts grounded in the supplied material |
| Revision | Creator feedback and a bounded review/revision loop |
| Planning | Suggested publication times based on preferences and the existing schedule |
| Approval | Review and approve individual posts with their destination and publication time |
| Scheduling | Durable scheduled posts with cancellation and rescheduling |
| Publishing | Direct integration with the selected platform |
| Visibility | A simple list of drafts, scheduled posts, and publishing results |

A minimal web interface is enough: submit a brief, review content and times, give feedback, approve, and inspect the schedule. A sophisticated calendar is outside the first release.

## Core user journey

1. Connect a social account and set voice, audience, timezone, and posting preferences.
2. Provide a content goal and source notes.
3. Receive draft posts and proposed publication times.
4. Revise, reject, or approve individual posts.
5. Let the service publish approved posts automatically at their scheduled times.
6. Check results and cancel or reschedule posts that are still pending.

## Product behavior and control

Drafts can be created and edited freely. Publication approval applies to a specific content version, account, and time. Changing an approved item requires approval of the updated plan.

Scheduling uses the creator's timezone and shows clear dates and times. Ambiguous requests require clarification. Suggested times reflect stated preferences; the MVP does not claim to predict optimal engagement.

Approved schedules survive application restarts. Publishing results distinguish success, failure, and an uncertain outcome. If a platform might have accepted a post before a connection failed, the system should resolve that uncertainty before attempting another publication.

The creator can cancel or reschedule pending posts. If publication has already begun, the interface explains that the change may be too late.

The agent should preserve the creator's voice, avoid inventing facts or personal achievements, and ask for missing details when they materially affect the content. Its revision loop has a limit so a request cannot run indefinitely.

## High-level system

- **Creator interface:** brief entry, content review, feedback, approval, and schedule/status views.
- **Agent:** interprets the brief, uses context tools, creates and revises drafts, and proposes a plan.
- **Application service and storage:** maintain profiles, sources, draft versions, approvals, schedules, and execution history.
- **Scheduler and publishing worker:** execute approved jobs at the intended times and record outcomes.
- **Platform integration:** handles account authorization and communication with the first social platform.

One agent is sufficient for the MVP. Planning, writing, and reviewing can be responsibilities within that agent rather than separate autonomous agents. The selected stack is FastAPI, Jinja2, PostgreSQL, SQLAlchemy async, Alembic and a separate worker; OpenAI is the selected model provider. Model suitability and the worker/deployment mechanism require evidence and design decisions in the [plan](../../specs/001-agentic-content-mvp/plan.md).

## What success looks like

The MVP is successful when a creator can complete the entire workflow on a real connected platform: submit a brief, get useful content, revise it, approve its publication times, and see the resulting posts published.

Content should fit the brief, preserve the supplied facts, and need a manageable amount of editing. The schedule should remain reliable across restarts, show failures clearly, and avoid blindly repeating uncertain publishing attempts.

Evaluation should consider content usefulness, editing effort, adherence to scheduling preferences, publishing reliability, response time, and operating cost. Numerical targets can be set after the platform and initial usage expectations are known.

Production acceptance also requires authenticated access, deterministic tool/approval permissions, baseline and held-out AI evaluations, input/privacy controls, bounded resource use, CI checks, actionable telemetry, capacity measurements, an observed restore/rollback drill and an approved live canary. Define numerical targets before final validation. A local demonstration is an intermediate milestone, not a production-readiness claim.

## Beyond the MVP

Potential extensions include additional platforms, image and video creation, web research, analytics-informed recommendations, recurring content plans, multiple brand profiles, team collaboration, and more autonomous workflows.

These extend the central idea: a creator gives direction, and the product helps turn it into a consistent publishing presence with understandable control over what happens.

## Open decisions

- Verified LinkedIn member publishing access and current supported API behavior.
- Model access and measured quality/cost suitability; monthly operating budget.
- Hosting provider/region, data retention constraints and measurable service/recovery targets.
- Authentication integration and durable-job implementation. Local development comes first; staging and a controlled production release are required later.

These choices affect implementation, but the product concept remains the same: agent-assisted creation and planning, followed by reliable execution of an approved publishing schedule.
