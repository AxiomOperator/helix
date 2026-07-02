# Agent Rules

This file defines repo-wide rules for coding agents working on Helix. Follow `docs/handoff.md` for product architecture and use this file for implementation conventions and required references.

## Required References

Read the relevant official docs before implementing features in these areas:

* Next.js parallel routes, important: https://nextjs.org/docs/app/api-reference/file-conventions/parallel-routes
* Next.js layouts and pages: https://nextjs.org/docs/app/getting-started/layouts-and-pages
* Next.js project structure: https://nextjs.org/docs/app/getting-started/project-structure
* Next.js server and client components: https://nextjs.org/docs/app/getting-started/server-and-client-components
* Next.js linking and navigating: https://nextjs.org/docs/app/getting-started/linking-and-navigating
* Next.js `error` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/error
* Next.js `layout` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/layout
* Next.js `loading` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/loading
* Next.js `not-found` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/not-found
* Next.js `page` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/page
* Next.js `template` file convention: https://nextjs.org/docs/app/api-reference/file-conventions/template
* Dragonfly documentation: https://www.dragonflydb.io/docs
* FastAPI and Typer: https://fastapi.tiangolo.com/#typer-the-fastapi-of-clis
* SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/

## General Rules

* Prefer small, explicit changes over broad rewrites.
* Keep security-sensitive flows policy-first: authenticate, authorize, evaluate policy, audit, then execute.
* Do not introduce arbitrary shell execution, browser terminal access, or approval bypasses unless the current phase explicitly requires them.
* Treat public IDs such as `node_...`, `job_...`, and `approval_...` as external API identifiers. Do not expose internal UUIDs unless explicitly required.
* Every write operation must have an audit path.
* Every job must pass through backend policy evaluation before dispatch.
* Do not trust frontend-provided risk levels, approval state, actor identity, or target authorization.

## Completion Workflow

After every implementation task, agents must:

* Run the relevant tests, checks, or build commands for the changed area.
* Update the checklist in `docs/handoff.md` with completed items and concise notes about what changed.
* Create a Git commit with a clear description of the work.
* Push committed changes to the configured remote when repository access is available.

If tests cannot be run, the handoff checklist notes and final response must clearly state why.

## Frontend Rules

* Use Next.js App Router conventions under `frontend/src/app`.
* Prefer Server Components by default. Add `'use client'` only for components that need browser-only APIs, local interactive state, effects, or event handlers.
* Keep route UI in `page.tsx`; put shared route chrome in `layout.tsx`; use `template.tsx` only when remount-on-navigation behavior is required.
* Use `loading.tsx` for route-level pending states, `error.tsx` for route-level recoverable errors, and `not-found.tsx` for missing resources.
* Use Next.js `Link` and router APIs for navigation. Do not use raw anchors for internal navigation unless there is a specific reason.
* Use parallel routes when a section needs independently loading or independently navigable panels, such as dashboards with primary content plus detail drawers, modals, or side panes. Parallel routes are important for this project because jobs, approvals, node details, and live output may need independent loading/error boundaries.
* Keep client-side state minimal. Use server data fetching and TanStack Query where live updates, polling, cache invalidation, or optimistic transitions are useful.
* Always show job status, risk level, approval state, and durable job output ordering clearly in the UI.
* Do not assume a job succeeded until the backend reports a terminal status.

## Backend Rules

* Use FastAPI for HTTP APIs and WebSockets.
* Use Typer for backend CLI commands such as admin user seeding, maintenance tasks, and development utilities.
* Use SQLAlchemy 2.0-style APIs. Prefer typed models, explicit sessions, and clear transaction boundaries.
* Use Alembic migrations for every database schema change.
* Use cookie sessions for dashboard/API user auth and enforce CSRF protection for unsafe methods.
* Agent WebSocket authentication must use the first-message `agent.auth` flow before accepting any other agent message.
* Approval records are authoritative for approval state. Do not add duplicate job-level approve/deny write paths.
* Persist job output as ordered durable events with per-job sequence numbers before or at the same time as broadcasting to clients.

## Data Store Rules

* Use PostgreSQL as the source of truth for durable application data.
* Use Dragonfly for Redis-compatible ephemeral workloads such as queues, pub/sub, cache, rate limiting, and transient coordination.
* Do not store audit logs, job history, approvals, or node inventory only in Dragonfly.
* Any Dragonfly-backed data required for recovery must be reconstructable from PostgreSQL.

## Agent Rules

* The Linux agent must reject unknown actions and validate parameters locally.
* The Linux agent must enforce timeouts and output limits.
* The Linux agent must never log secrets, raw tokens, command credentials, or sensitive environment values.
* The Linux agent must not execute arbitrary shell commands except through the explicitly approved `shell.run` action in a later phase.
* The Linux agent must continue running if one job fails and must reconnect automatically after transport failures.

## Testing Rules

* Add tests with behavior changes, especially for auth, policy, approvals, audit, job lifecycle, and agent protocol handling.
* Test CSRF enforcement for unsafe cookie-authenticated requests.
* Test first-message agent authentication for accepted, rejected, and wrong-first-message flows.
* Test ordered job event persistence and replay.
* For frontend routes, cover loading, error, not-found, and permission-sensitive states when practical.
