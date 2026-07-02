# Linux Command Center — Developer Handoff

## 1. Project Overview

### 1.1 Purpose

Build a custom Linux fleet management command center that allows administrators to manage Linux servers from a central web dashboard.

The system will provide:

* Fleet inventory
* Live node status
* Health monitoring
* System service management
* Package/update visibility
* Controlled remote actions
* Approval workflows for risky actions
* Job execution and output streaming
* Audit logging
* Optional controlled terminal access in a later phase

This is not a wrapper around existing tools. The product is a custom control plane, dashboard, and Linux agent system.

---

## 2. Core Design Principle

The system must be **policy-first**, not shell-first.

Do not design the platform as:

```text
User types command
Backend forwards command
Agent runs command
```

Design it as:

```text
User requests an action
Control plane checks policy
Approval is required when appropriate
Agent executes a bounded operation
Output is streamed and stored
Audit trail records everything
```

This distinction is critical.

The command center should eventually support arbitrary shell access, but only as a high-risk, audited, approval-gated feature.

---

## 3. High-Level Architecture

```text
┌──────────────────────────────────────────────┐
│                 Web Dashboard                 │
│  Next.js / TypeScript                         │
│  Nodes, jobs, approvals, logs, audit          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              Control Plane API                │
│  FastAPI                                      │
│  Auth, RBAC, policy, jobs, audit              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              Agent Transport Layer            │
│  Agent outbound WebSocket                     │
│  Heartbeats, job dispatch, output streams     │
└──────────────────────┬───────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Linux Agent │  │ Linux Agent │  │ Linux Agent │
│ Fedora      │  │ Ubuntu      │  │ Rocky/Alma  │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## 4. Recommended Technology Stack

### 4.1 Frontend

Use:

```text
Next.js
TypeScript
App Router
TanStack Query
Zustand or equivalent lightweight state store
shadcn/ui or similar component system
xterm.js later for browser terminal
```

### 4.2 Backend

Use:

```text
FastAPI
PostgreSQL
SQLAlchemy
Alembic
DragonFlyDB
WebSockets
Cookie session auth
```

### 4.3 Linux Agent

Use:

```text
Go
systemd service
Outbound WebSocket transport
Local action handlers
Structured JSON protocol
```

Reasoning:

* Go gives fast iteration.
* Single static binaries are easy to distribute.
* Cross-distro Linux support is straightforward.
* WebSocket and process execution support are mature.

Rust may be considered later if the project needs stronger memory-safety guarantees, but Go is the recommended MVP agent language.

### 4.4 Deployment

Control plane:

```text
Docker Compose
PostgreSQL container
DragonFlyDB container
Backend container
Next.js frontend container
```

Agent:

```text
systemd service installed directly on each Linux host
```

---

## 5. Repository Layout

```text
linux-command-center/
  README.md
  docker-compose.yml
  .env.example

  backend/
    pyproject.toml
    alembic.ini
    alembic/
    app/
      main.py
      config.py
      db/
        session.py
        base.py
      models/
        user.py
        node.py
        node_interface.py
        node_metric.py
        service.py
        job.py
        job_event.py
        approval.py
        audit.py
        enrollment.py
      schemas/
        user.py
        node.py
        job.py
        approval.py
        audit.py
        agent.py
      api/
        auth.py
        nodes.py
        jobs.py
        approvals.py
        audit.py
        agents.py
      services/
        auth_service.py
        node_service.py
        job_service.py
        policy_service.py
        approval_service.py
        audit_service.py
        agent_session_service.py
      websocket/
        dashboard_ws.py
        agent_ws.py
      policies/
        actions.py
        risk.py
        evaluator.py
      security/
        password.py
        tokens.py
        rbac.py

  frontend/
    package.json
    next.config.ts
    tsconfig.json
    src/
      app/
        layout.tsx
        page.tsx
        login/
          page.tsx
        nodes/
          page.tsx
          [nodeId]/
            page.tsx
        jobs/
          page.tsx
          [jobId]/
            page.tsx
        approvals/
          page.tsx
        audit/
          page.tsx
      components/
      features/
        auth/
        dashboard/
        nodes/
        jobs/
        approvals/
        audit/
        settings/
        terminal/
      lib/
        api.ts
        websocket.ts
        types.ts

  agent/
    go.mod
    cmd/
      command-agent/
        main.go
    internal/
      config/
      identity/
      enroll/
      transport/
      heartbeat/
      inventory/
      executor/
      actions/
        system/
        services/
        packages/
        logs/
        shell/
      metrics/
      systemd/
      packages/
      logging/
    packaging/
      systemd/
        linux-command-agent.service
      install.sh

  docs/
    architecture.md
    agent-protocol.md
    security-model.md
    job-lifecycle.md
    api.md
    deployment.md
    developer-setup.md
```

---

# 6. Core Concepts

## 6.1 Node

A node is a managed Linux machine.

Nodes have an internal UUID primary key and an external prefixed public ID, such as `node_01hxyz...`. APIs, UI routes, audit targets, and agent protocol messages must use the public ID unless explicitly documented otherwise.

Each node has:

```text
Unique node ID
Hostname
Machine ID
Operating system
Kernel version
IP addresses
Site
Role
Environment
Agent version
Online/offline state
Last seen timestamp
```

## 6.2 Agent

The agent is the local executable running on each Linux box.

The agent is responsible for:

```text
Enrollment
Heartbeat
Inventory collection
Metric collection
Systemd service inspection
Package update inspection
Controlled action execution
Output streaming
Job completion reporting
```

## 6.3 Job

A job is a requested action against one or more nodes.

Jobs have an internal UUID primary key and an external prefixed public ID, such as `job_01hxyz...`. APIs, UI routes, audit targets, and agent protocol messages must use the public ID unless explicitly documented otherwise.

Examples:

```text
Check system info
Restart nginx
Tail journal logs
Check pending updates
Reboot node
Run approved shell command
```

Each job must have:

```text
Requester
Target
Action
Parameters
Risk level
Status
Approval state
Output events
Exit code
Timestamps
Audit trail
```

## 6.4 Action

An action is a named operation the system supports.

Examples:

```text
system.info
system.reboot
service.status
service.restart
logs.journal_tail
packages.check_updates
packages.upgrade_all
shell.run
terminal.open
```

Actions must be defined in the backend policy catalog.

Agents should only execute supported actions.

## 6.5 Approval

Certain jobs require approval before execution.

The `approvals` table is the authoritative source for approval state. Job status may reflect approval state for filtering and lifecycle display, but approval decisions must be written through approval records.

Approval is based on:

```text
Risk level
User role
Target group
Action type
System policy
```

## 6.6 Audit Log

The audit log is the append-only application-level record of meaningful activity for the MVP. Application code must never update or delete audit events.

Audit events include:

```text
Login
Logout
Node enrollment
Node deletion
Job requested
Job approved
Job denied
Job dispatched
Job started
Job completed
Job failed
Terminal opened
File modified
Settings changed
```

---

# 7. Risk Model

The project must implement risk levels from the start.

## 7.1 Risk Levels

```text
read
low
medium
high
critical
full_access
```

## 7.2 Risk Definitions

### read

Read-only operations.

Examples:

```text
View node inventory
View logs
View metrics
Check service status
Check update availability
```

Approval required:

```text
No
```

### low

Safe operational actions with minimal impact.

Examples:

```text
Refresh inventory
Run health check
Run package metadata refresh
```

Approval required:

```text
No
```

### medium

Actions that may temporarily impact a local service.

Examples:

```text
Restart non-critical service
Reload nginx
Restart a container
```

Approval required:

```text
Configurable
```

### high

Actions that may impact host availability or system configuration.

Examples:

```text
Reboot server
Install updates
Modify firewall
Write config file
Restart critical service
```

Approval required:

```text
Yes by default
```

### critical

Actions that can cause major outage, data loss, or privilege/security changes.

Examples:

```text
Run arbitrary shell command
Delete files
Modify SSH config
Modify sudoers
Change network config
Change disk layout
```

Approval required:

```text
Yes
```

### full_access

Break-glass unrestricted administrative access.

Examples:

```text
Unrestricted shell
Approval bypass mode
Emergency admin override
```

Approval required:

```text
System policy dependent, but must be heavily audited
```

---

# 8. Job Lifecycle

Implement the following lifecycle:

```text
requested
policy_check
awaiting_approval
approved
denied
queued
dispatched
started
running
completed
failed
expired
cancelled
```

## 8.1 Lifecycle Rules

### requested

Job was created by a user or scheduled task.

### policy_check

Backend is evaluating whether the job is allowed.

### awaiting_approval

Job is valid but requires approval.

### approved

A permitted approver approved the job.

### denied

An approver rejected the job.

### queued

Job is ready for execution.

### dispatched

Control plane sent the job to the agent.

### started

Agent acknowledged the job and began execution.

### running

Agent is actively streaming job output.

### completed

Agent completed successfully.

### failed

Agent failed to complete the job.

### expired

Approval or job execution window expired.

### cancelled

User or system cancelled the job.

---

# 9. Database Schema

## 9.1 users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'operator',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 9.2 nodes

```sql
CREATE TABLE nodes (
    id UUID PRIMARY KEY,
    public_id TEXT UNIQUE NOT NULL,
    hostname TEXT NOT NULL,
    fqdn TEXT,
    machine_id TEXT UNIQUE,
    os_name TEXT,
    os_version TEXT,
    kernel_version TEXT,
    architecture TEXT,
    primary_ip INET,
    site TEXT,
    environment TEXT,
    role TEXT,
    agent_version TEXT,
    status TEXT NOT NULL DEFAULT 'unknown',
    last_seen_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 9.3 node_interfaces

```sql
CREATE TABLE node_interfaces (
    id UUID PRIMARY KEY,
    node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    mac_address TEXT,
    ip_address INET,
    cidr TEXT,
    is_primary BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 9.4 node_metrics

```sql
CREATE TABLE node_metrics (
    id BIGSERIAL PRIMARY KEY,
    node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    cpu_percent NUMERIC,
    memory_percent NUMERIC,
    disk_percent NUMERIC,
    load_1 NUMERIC,
    load_5 NUMERIC,
    load_15 NUMERIC,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 9.5 services

```sql
CREATE TABLE services (
    id UUID PRIMARY KEY,
    node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    active_state TEXT,
    sub_state TEXT,
    unit_file_state TEXT,
    description TEXT,
    last_checked_at TIMESTAMPTZ,
    UNIQUE(node_id, name)
);
```

## 9.6 enrollment_tokens

```sql
CREATE TABLE enrollment_tokens (
    id UUID PRIMARY KEY,
    token_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    allowed_site TEXT,
    allowed_environment TEXT,
    max_uses INTEGER,
    use_count INTEGER NOT NULL DEFAULT 0,
    expires_at TIMESTAMPTZ,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    revoked_at TIMESTAMPTZ
);
```

## 9.7 agent_credentials

```sql
CREATE TABLE agent_credentials (
    id UUID PRIMARY KEY,
    node_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    issued_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ
);
```

## 9.8 jobs

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    public_id TEXT UNIQUE NOT NULL,
    requested_by UUID NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    status TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_node_id UUID REFERENCES nodes(id),
    target_selector JSONB NOT NULL DEFAULT '{}',
    params JSONB NOT NULL DEFAULT '{}',
    approval_required BOOLEAN NOT NULL DEFAULT false,
    dispatched_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    exit_code INTEGER,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## 9.9 job_events

```sql
CREATE TABLE job_events (
    id BIGSERIAL PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    sequence BIGINT NOT NULL,
    event_type TEXT NOT NULL,
    stream TEXT,
    message TEXT,
    chunk_bytes INTEGER,
    truncated BOOLEAN NOT NULL DEFAULT false,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(job_id, sequence)
);
```

`sequence` is a monotonically increasing per-job event number used for durable ordered replay in the UI and audit trail. Job output must be persisted before or at the same time it is broadcast to dashboard clients.

## 9.10 approvals

```sql
CREATE TABLE approvals (
    id UUID PRIMARY KEY,
    public_id TEXT UNIQUE NOT NULL,
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    requested_by UUID NOT NULL REFERENCES users(id),
    approved_by UUID REFERENCES users(id),
    denied_by UUID REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'pending',
    reason TEXT,
    resolution_reason TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at TIMESTAMPTZ
);
```

## 9.11 audit_log

```sql
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    actor_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    result TEXT,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

# 10. API Contract

Path parameters named `{node_id}`, `{job_id}`, and `{approval_id}` refer to external prefixed public IDs, not internal database UUIDs.

## 10.1 Auth

```text
POST /auth/login
POST /auth/logout
GET  /auth/csrf
GET  /me
```

## 10.2 Nodes

```text
GET    /nodes
GET    /nodes/{node_id}
PATCH  /nodes/{node_id}
DELETE /nodes/{node_id}

GET    /nodes/{node_id}/metrics
GET    /nodes/{node_id}/services
GET    /nodes/{node_id}/jobs
GET    /nodes/{node_id}/logs
```

## 10.3 Enrollment

```text
POST /enrollment-tokens
GET  /enrollment-tokens
POST /agents/enroll
```

## 10.4 Jobs

```text
POST /jobs
GET  /jobs
GET  /jobs/{job_id}
POST /jobs/{job_id}/cancel
```

Job approval and denial must use the approval endpoints. Do not add duplicate job-level approve or deny endpoints.

## 10.5 Approvals

```text
GET /approvals
GET /approvals/{approval_id}
POST /approvals/{approval_id}/approve
POST /approvals/{approval_id}/deny
```

## 10.6 Audit

```text
GET /audit
```

## 10.7 WebSockets

```text
WS /ws/dashboard
WS /ws/agent
WS /ws/jobs/{job_id}
WS /ws/terminal/{session_id}
```

---

# 11. Agent Protocol

## 11.1 Agent Authentication

The agent must authenticate as the first message after opening `/ws/agent`. The backend must reject and close the connection if any other message is received before successful authentication.

```json
{
  "type": "agent.auth",
  "node_id": "node_01hxyzabc123",
  "agent_token": "secret"
}
```

On success, the control plane sends:

```json
{
  "type": "agent.auth.accepted"
}
```

On failure, the control plane sends an error when safe and closes the connection:

```json
{
  "type": "agent.auth.rejected",
  "error": "invalid credentials"
}
```

The raw agent token must never be logged. The backend stores only the token hash.

## 11.2 Agent Hello

Agent sends after successful authentication:

```json
{
  "type": "agent.hello",
  "node_id": "node_01hxyzabc123",
  "agent_version": "0.1.0",
  "protocol_version": "0.1"
}
```

## 11.3 Heartbeat

```json
{
  "type": "agent.heartbeat",
  "node_id": "node_01hxyzabc123",
  "timestamp": "2026-07-01T20:00:00Z",
  "metrics": {
    "cpu_percent": 12.4,
    "memory_percent": 61.2,
    "disk_percent": 74.9,
    "load_1": 0.45,
    "load_5": 0.51,
    "load_15": 0.49
  },
  "health": {
    "failed_units": 0,
    "pending_updates": 18,
    "uptime_seconds": 384920
  }
}
```

## 11.4 Inventory Report

```json
{
  "type": "agent.inventory",
  "node_id": "node_01hxyzabc123",
  "hostname": "fedora-ai-01",
  "fqdn": "fedora-ai-01.local",
  "machine_id": "abc123",
  "os_name": "Fedora",
  "os_version": "44",
  "kernel_version": "6.x",
  "architecture": "x86_64",
  "interfaces": [
    {
      "name": "eth0",
      "mac_address": "00:11:22:33:44:55",
      "ip_address": "192.168.1.50",
      "cidr": "192.168.1.50/24",
      "is_primary": true
    }
  ]
}
```

## 11.5 Job Start

Control plane sends:

```json
{
  "type": "job.start",
  "job_id": "job_01hxyzdef456",
  "action": "service.restart",
  "params": {
    "service": "nginx"
  },
  "timeout_seconds": 120
}
```

## 11.6 Job Started

Agent sends:

```json
{
  "type": "job.started",
  "job_id": "job_01hxyzdef456"
}
```

## 11.7 Job Output

```json
{
  "type": "job.output",
  "job_id": "job_01hxyzdef456",
  "sequence": 3,
  "stream": "stdout",
  "message": "Restarting nginx...",
  "truncated": false
}
```

`sequence` is monotonic per job. The backend must persist output events with their sequence number and use `(job_id, sequence)` for durable ordered replay. If output exceeds the configured limit, the final persisted output event must set `truncated` to `true`.

## 11.8 Job Completed

```json
{
  "type": "job.completed",
  "job_id": "job_01hxyzdef456",
  "exit_code": 0
}
```

## 11.9 Job Failed

```json
{
  "type": "job.failed",
  "job_id": "job_01hxyzdef456",
  "exit_code": 1,
  "error": "systemctl restart nginx failed"
}
```

---

# 12. Action Catalog

The backend must maintain an action catalog.

## 12.1 Initial Actions

### system.info

Risk:

```text
read
```

Description:

```text
Return OS, kernel, uptime, CPU, memory, disk, and basic host information.
```

### system.reboot

Risk:

```text
high
```

Approval:

```text
Required by default
```

Description:

```text
Reboot the target node.
```

### service.list

Risk:

```text
read
```

Description:

```text
List systemd services.
```

### service.status

Risk:

```text
read
```

Parameters:

```json
{
  "service": "nginx"
}
```

### service.restart

Risk:

```text
medium
```

Parameters:

```json
{
  "service": "nginx"
}
```

### service.stop

Risk:

```text
high
```

Parameters:

```json
{
  "service": "nginx"
}
```

### service.start

Risk:

```text
medium
```

Parameters:

```json
{
  "service": "nginx"
}
```

### logs.journal_tail

Risk:

```text
read
```

Parameters:

```json
{
  "unit": "nginx",
  "lines": 200
}
```

### packages.check_updates

Risk:

```text
read
```

Description:

```text
Check available package updates.
```

### packages.upgrade_all

Risk:

```text
high
```

Approval:

```text
Required by default
```

Description:

```text
Apply all available package updates.
```

### shell.run

Risk:

```text
critical
```

Approval:

```text
Required
```

Description:

```text
Run arbitrary shell command with timeout and output capture.
```

---

# 13. Backend Implementation Requirements

## 13.1 Auth

MVP auth may use local users.

MVP web auth must use server-managed cookie sessions. Session cookies must be HTTP-only, same-site, secure in production, and paired with CSRF protection for unsafe methods.

Required:

```text
Password hashing
Login endpoint
Cookie session creation and invalidation
CSRF protection for unsafe methods
Role field
Active/inactive users
```

Roles:

```text
viewer
operator
admin
break_glass_admin
```

## 13.2 RBAC

Initial RBAC rules:

| Role              | Capabilities                      |
| ----------------- | --------------------------------- |
| viewer            | Read nodes, metrics, logs, jobs   |
| operator          | Run read/low/medium actions       |
| admin             | Run high actions, approve jobs    |
| break_glass_admin | Use critical/full-access features |

## 13.3 Policy Engine

The policy engine must evaluate every job before dispatch.

Policy inputs:

```text
User
Role
Action
Risk level
Target node
Target group
Approval requirement
System settings
```

Policy outputs:

```text
allow
deny
approval_required
```

## 13.4 Agent Session Manager

Maintain an in-memory map of connected agents:

```text
node_id -> websocket connection
```

Responsibilities:

```text
Track connected nodes
Mark nodes online
Mark nodes offline on disconnect
Dispatch jobs to agents
Receive heartbeat
Receive job output
Broadcast updates to dashboard clients
```

## 13.5 Job Service

The job service must:

```text
Create jobs
Evaluate policy
Create approval records when needed
Queue approved jobs
Dispatch to connected agents
Store durable ordered job events
Update job status
Notify dashboard clients
```

Job output events must be persisted with per-job sequence numbers before or at the same time they are broadcast to dashboard clients.

## 13.6 Audit Service

Every sensitive action must call the audit service.

Audit events are append-only in the MVP. Application code must not update or delete audit log rows.

Audit events should be written for:

```text
auth.login
auth.logout
node.enrolled
node.updated
node.deleted
job.requested
job.policy_allowed
job.policy_denied
job.approval_requested
job.approved
job.denied
job.dispatched
job.started
job.completed
job.failed
terminal.opened
settings.updated
```

---

# 14. Agent Implementation Requirements

## 14.1 Agent Config

Example config:

```toml
server_url = "https://command-center.example.com"
node_id = "node_abc123"
agent_token = "secret"
heartbeat_interval_seconds = 15
inventory_interval_seconds = 300
log_level = "info"
```

Path:

```text
/etc/linux-command-agent/config.toml
```

## 14.2 Agent Service

Systemd unit:

```ini
[Unit]
Description=Linux Command Center Agent
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/linux-command-agent
Restart=always
RestartSec=5
User=root

[Install]
WantedBy=multi-user.target
```

## 14.3 Agent Startup Flow

```text
Load config
Validate node identity
Connect to control plane WebSocket
Send `agent.auth` as the first WebSocket message
Wait for `agent.auth.accepted`
Send agent.hello
Start heartbeat loop
Start inventory loop
Listen for jobs
Execute supported actions
Stream outputs
Report completion/failure
Reconnect on disconnect
```

## 14.4 Agent Safety Requirements

The agent must:

```text
Reject unknown actions
Validate parameters
Enforce timeouts
Limit output size
Avoid shell execution except for shell.run
Capture stdout/stderr
Return clear exit codes
Log locally
Never expose stored token in logs
```

## 14.5 Package Manager Detection

Agent should detect:

```text
dnf
yum
apt
pacman
zypper
```

Initial support priority:

```text
dnf
apt
yum
```

---

# 15. Frontend Requirements

## 15.1 Pages

### Login

Requirements:

```text
Username/email
Password
Login error handling
Session persistence
```

### Overview

Show:

```text
Total nodes
Online nodes
Offline nodes
Warning nodes
Failed services
Pending updates
Running jobs
Pending approvals
Recent failures
```

### Nodes

Table columns:

```text
Status
Hostname
Site
Environment
Role
OS
Kernel
Primary IP
CPU
Memory
Disk
Pending Updates
Last Seen
```

Filters:

```text
Status
Site
Environment
Role
OS
Tag
```

### Node Detail

Tabs:

```text
Summary
Metrics
Network
Services
Packages
Logs
Jobs
Audit
Actions
```

### Jobs

Views:

```text
All jobs
Running jobs
Failed jobs
Completed jobs
Pending approval
```

Job detail must show:

```text
Action
Target
Requester
Status
Risk level
Approval state
Start time
Duration
Output stream
Exit code
Error message
```

### Approvals

Approval card must show:

```text
Requested by
Action
Target
Risk level
Parameters
Reason
Approve button
Deny button
```

### Audit

Table columns:

```text
Timestamp
Actor
Action
Target
Result
IP
Details
```

---

# 16. Security Requirements

## 16.1 Mandatory Security Controls

The system must implement:

```text
Authentication
CSRF protection for cookie-authenticated unsafe requests
RBAC
Action policy checks
Agent authentication
Audit logging
Approval workflow
Output capture
Job timeout
Parameter validation
Token hashing at rest
```

## 16.2 Forbidden MVP Behavior

Do not allow:

```text
Anonymous access
Unauthenticated agents
Blind shell command execution
Commands without job records
Actions without audit entries
Agents accepting jobs from unknown servers
Plaintext token logging
Approval bypass except explicit break-glass flow
```

## 16.3 Web Authentication

The MVP must use server-managed cookie sessions for dashboard/API users.

Cookie/session requirements:

```text
HTTP-only session cookie
SameSite session cookie
Secure cookie flag in production
Server-side session invalidation on logout
CSRF token required for unsafe methods
```

## 16.4 Agent Authentication

MVP may use a long-lived agent token.

For the MVP, the agent authenticates to `/ws/agent` by sending `agent.auth` as the first WebSocket message. The backend must reject any unauthenticated connection that sends another message type first.

Token storage:

```text
Store raw token only on agent
Store hash in database
Rotate later
```

Future improvement:

```text
mTLS
short-lived agent credentials
automatic token rotation
```

## 16.5 Approval Policy

Default approval requirements:

| Risk        | Approval                |
| ----------- | ----------------------- |
| read        | No                      |
| low         | No                      |
| medium      | Optional                |
| high        | Yes                     |
| critical    | Yes                     |
| full_access | Yes or break-glass only |

---

# 17. Phase Plan

## Phase 0 — Project Bootstrap

### Goal

Create the base repository, development environment, and skeleton services.

### Backend Checklist

* [x] Create FastAPI app
* [x] Add config loader
* [x] Add PostgreSQL connection
* [x] Add SQLAlchemy
* [x] Add Alembic migrations
* [x] Add health endpoint
* [x] Add structured logging
* [x] Add `.env.example`

### Frontend Checklist

* [x] Create Next.js TypeScript app
* [x] Add App Router routes
* [x] Add API client
* [x] Add base layout
* [x] Add login page placeholder
* [x] Add dashboard page placeholder

### Agent Checklist

* [x] Create Go module
* [x] Add config loader
* [x] Add basic CLI
* [x] Add version command
* [x] Add systemd unit template
* [x] Add install script placeholder

### DevOps Checklist

* [x] Create Docker Compose
* [x] Add backend service
* [x] Add frontend service
* [x] Add PostgreSQL
* [x] Add Redis
* [x] Add local development README

### Acceptance Criteria

* [x] `docker compose up` starts backend, frontend, database, and Redis
* [x] Backend health endpoint returns OK
* [x] Frontend loads in browser
* [x] Agent binary builds locally

### Phase 0 Notes

Implemented the Phase 0 skeleton only: FastAPI health service, Pydantic Settings config, SQLAlchemy/Alembic scaffolding, structured logging, Next.js placeholder routes, basic frontend API helper, Go agent CLI/config/version scaffold, systemd unit template, safe install placeholder, Docker Compose, `.env.example`, `.gitignore`, and README.

Validation completed with `docker compose up --build -d`, `curl http://localhost:8000/health`, `curl http://localhost:3000`, `docker compose ps`, and `cd agent && go build -o command-agent ./cmd/command-agent && ./command-agent version`. Frontend Docker install reports two moderate npm audit findings in dependencies; no Phase 0 runtime validation failed.

---

## Phase 1 — Auth, Users, and Base UI

### Goal

Implement local login and basic role-aware dashboard shell.

### Backend Checklist

* [ ] Create users table
* [ ] Add password hashing
* [ ] Add seed admin user
* [ ] Implement login endpoint
* [ ] Implement logout endpoint
* [ ] Implement CSRF token endpoint and validation
* [ ] Implement `/me`
* [ ] Add auth middleware/dependency
* [ ] Add role field
* [ ] Add audit event for login
* [ ] Add audit event for logout

### Frontend Checklist

* [ ] Implement login form
* [ ] Use cookie session securely
* [ ] Send CSRF token on unsafe requests
* [ ] Implement authenticated routes
* [ ] Add sidebar navigation
* [ ] Add topbar with current user
* [ ] Add logout button
* [ ] Add role-aware navigation visibility

### Acceptance Criteria

* [ ] Admin can log in
* [ ] Invalid login fails cleanly
* [ ] Authenticated API calls work
* [ ] Unauthenticated users are redirected to login
* [ ] Login/logout events appear in audit log

---

## Phase 2 — Node Enrollment and Agent Connectivity

### Goal

Allow Linux agents to enroll and connect to the control plane.

### Backend Checklist

* [ ] Create nodes table
* [ ] Create enrollment_tokens table
* [ ] Create agent_credentials table
* [ ] Add endpoint to create enrollment token
* [ ] Add agent enrollment endpoint
* [ ] Hash enrollment tokens at rest
* [ ] Issue agent credential after enrollment
* [ ] Implement `/ws/agent`
* [ ] Authenticate agent WebSocket connection
* [ ] Add agent session manager
* [ ] Mark node online on connect
* [ ] Mark node offline on disconnect
* [ ] Add node enrollment audit event

### Agent Checklist

* [ ] Implement `enroll` command
* [ ] Send machine ID, hostname, OS, kernel, architecture
* [ ] Store node ID and agent token in config
* [ ] Connect to `/ws/agent`
* [ ] Send `agent.auth` as first WebSocket message
* [ ] Send `agent.hello`
* [ ] Reconnect on disconnect
* [ ] Log connection status

### Frontend Checklist

* [ ] Add enrollment token page
* [ ] Add node list page
* [ ] Show online/offline status
* [ ] Show last seen timestamp
* [ ] Add empty-state UI for no nodes

### Acceptance Criteria

* [ ] Admin can create enrollment token
* [ ] Agent can enroll successfully
* [ ] Enrolled node appears in dashboard
* [ ] Node shows online when agent is connected
* [ ] Node shows offline when agent disconnects

---

## Phase 3 — Heartbeat, Inventory, and Metrics

### Goal

Collect real node state and display it in the dashboard.

### Backend Checklist

* [ ] Add heartbeat handler
* [ ] Add inventory handler
* [ ] Add node_metrics table
* [ ] Add node_interfaces table
* [ ] Store heartbeat metrics
* [ ] Store inventory data
* [ ] Update last_seen_at from heartbeat
* [ ] Add node metrics API
* [ ] Add node interface API

### Agent Checklist

* [ ] Collect CPU percentage
* [ ] Collect memory percentage
* [ ] Collect disk percentage
* [ ] Collect load averages
* [ ] Collect uptime
* [ ] Collect failed systemd unit count
* [ ] Collect pending update count
* [ ] Send heartbeat every configured interval
* [ ] Collect OS inventory
* [ ] Collect network interfaces
* [ ] Send inventory every configured interval

### Frontend Checklist

* [ ] Update node table with CPU/memory/disk
* [ ] Add node detail summary
* [ ] Add metrics cards
* [ ] Add network interface table
* [ ] Add health/warning indicators

### Acceptance Criteria

* [ ] Dashboard shows real CPU/memory/disk data
* [ ] Dashboard shows uptime
* [ ] Dashboard shows failed unit count
* [ ] Dashboard shows pending update count
* [ ] Node detail shows network interfaces

---

## Phase 4 — Job System and Safe Actions

### Goal

Implement the job system and initial safe actions.

### Backend Checklist

* [ ] Create jobs table
* [ ] Create job_events table with per-job sequence numbers
* [ ] Implement action catalog
* [ ] Implement policy evaluator
* [ ] Implement job creation endpoint
* [ ] Implement job dispatch to connected agent
* [ ] Implement job event ingestion
* [ ] Implement job status updates
* [ ] Add job list endpoint
* [ ] Add job detail endpoint
* [ ] Add WebSocket stream for job output
* [ ] Add audit events for job lifecycle

### Agent Checklist

* [ ] Receive `job.start`
* [ ] Validate action
* [ ] Implement `system.info`
* [ ] Implement `service.list`
* [ ] Implement `service.status`
* [ ] Implement `logs.journal_tail`
* [ ] Send `job.started`
* [ ] Stream stdout/stderr events with per-job sequence numbers
* [ ] Send `job.completed`
* [ ] Send `job.failed` on error
* [ ] Enforce timeout
* [ ] Enforce output size limit

### Frontend Checklist

* [ ] Add action buttons on node detail
* [ ] Add jobs page
* [ ] Add job detail page
* [ ] Add live output viewer
* [ ] Add status badges
* [ ] Add recent jobs panel on node detail

### Acceptance Criteria

* [ ] User can run `system.info`
* [ ] User can list services
* [ ] User can check service status
* [ ] User can tail journal logs
* [ ] Job output streams live
* [ ] Job results are stored
* [ ] Audit log records job activity

---

## Phase 5 — Approval Engine

### Goal

Add approval gates for high-risk and critical actions before service restart is included in the MVP.

### Backend Checklist

* [ ] Create approvals table
* [ ] Add approval policy rules
* [ ] Create approval when required
* [ ] Block dispatch until approved
* [ ] Implement approve endpoint
* [ ] Implement deny endpoint
* [ ] Add approval expiration
* [ ] Add approver authorization check
* [ ] Add audit events for approval/denial
* [ ] Prevent requester from approving own job unless policy allows

### Frontend Checklist

* [ ] Add approvals page
* [ ] Add approval count badge
* [ ] Add approval cards
* [ ] Show action, target, requester, risk, params
* [ ] Add approve button
* [ ] Add deny button
* [ ] Add denial reason input
* [ ] Show approval state on job detail

### Acceptance Criteria

* [ ] High-risk job enters awaiting approval
* [ ] Job does not dispatch before approval
* [ ] Admin can approve job
* [ ] Admin can deny job
* [ ] Denied job never runs
* [ ] Approval/denial is audited

---

## Phase 6 — Service Management

### Goal

Allow controlled service operations after the approval engine is in place.

### Backend Checklist

* [ ] Add `service.restart`
* [ ] Add `service.start`
* [ ] Add `service.stop`
* [ ] Add service risk levels
* [ ] Add service action parameter validation
* [ ] Store service action audit records

### Agent Checklist

* [ ] Implement systemd restart
* [ ] Implement systemd start
* [ ] Implement systemd stop
* [ ] Validate service names
* [ ] Return systemctl output
* [ ] Return failure reason on failed operation
* [ ] Refresh service status after operation

### Frontend Checklist

* [ ] Add services tab
* [ ] Add restart/start/stop controls
* [ ] Add confirmation modal for restart/stop
* [ ] Show active/sub/unit state
* [ ] Refresh services after action

### Acceptance Criteria

* [ ] Operator can restart allowed services
* [ ] Service action produces job record
* [ ] Job output shows systemctl result
* [ ] Service state refreshes after action
* [ ] Failed service action shows useful error

---

## Phase 7 — Package Management

### Goal

Add cross-distro package update visibility and patching.

### Backend Checklist

* [ ] Add package manager metadata to node
* [ ] Add `packages.check_updates`
* [ ] Add `packages.upgrade_all`
* [ ] Add `packages.install`
* [ ] Add `packages.remove`
* [ ] Mark upgrade/install/remove as high risk
* [ ] Require approval for upgrade/install/remove
* [ ] Store package job output

### Agent Checklist

* [ ] Detect package manager
* [ ] Implement dnf update check
* [ ] Implement apt update check
* [ ] Implement yum update check
* [ ] Implement dnf upgrade
* [ ] Implement apt upgrade
* [ ] Implement yum upgrade
* [ ] Stream package operation output
* [ ] Handle package lock errors
* [ ] Return reboot-required indicator where available

### Frontend Checklist

* [ ] Add packages tab
* [ ] Show package manager
* [ ] Show pending updates
* [ ] Add check updates button
* [ ] Add upgrade all button
* [ ] Show approval requirement
* [ ] Show package operation output

### Acceptance Criteria

* [ ] Dashboard shows pending update count
* [ ] User can check updates on a node
* [ ] Upgrade job requires approval
* [ ] Approved upgrade runs on agent
* [ ] Package output streams live
* [ ] Package failure is clearly reported

---

## Phase 8 — Groups, Tags, and Bulk Jobs

### Goal

Allow managing nodes as groups instead of one host at a time.

### Backend Checklist

* [ ] Add node tags
* [ ] Add node groups
* [ ] Add group membership table
* [ ] Add target selectors for jobs
* [ ] Resolve selector to nodes at job creation
* [ ] Create child jobs per node
* [ ] Track parent job status
* [ ] Add bulk job rate limiting
* [ ] Add concurrency control

### Frontend Checklist

* [ ] Add tag/group management
* [ ] Add group filter on node list
* [ ] Add bulk action UI
* [ ] Add bulk job progress page
* [ ] Show per-node success/failure

### Acceptance Criteria

* [ ] User can assign tags to nodes
* [ ] User can create groups
* [ ] User can run action against selected nodes
* [ ] User can run action against group
* [ ] Bulk job shows per-node status
* [ ] Bulk job respects concurrency limit

---

## Phase 9 — Controlled Shell Command

### Goal

Add arbitrary shell command execution with strict controls.

### Backend Checklist

* [ ] Add `shell.run`
* [ ] Mark as critical
* [ ] Require approval
* [ ] Add command reason field
* [ ] Add timeout configuration
* [ ] Add output size limit
* [ ] Add shell command audit metadata
* [ ] Add optional denylist
* [ ] Add policy to restrict role access

### Agent Checklist

* [ ] Implement shell execution
* [ ] Use controlled process runner
* [ ] Enforce timeout
* [ ] Capture stdout/stderr separately
* [ ] Limit output size
* [ ] Return exit code
* [ ] Never run shell command without job ID
* [ ] Log local execution metadata

### Frontend Checklist

* [ ] Add shell command UI
* [ ] Require reason input
* [ ] Show risk warning
* [ ] Show approval requirement
* [ ] Show command preview before submit
* [ ] Stream output live

### Acceptance Criteria

* [ ] Shell command always requires approval
* [ ] Shell command cannot run without reason
* [ ] Shell command output streams live
* [ ] Timeout works
* [ ] Exit code is captured
* [ ] Audit log includes command metadata

---

## Phase 10 — Browser Terminal

### Goal

Add controlled interactive terminal sessions.

### Backend Checklist

* [ ] Add terminal session model
* [ ] Add `terminal.open`
* [ ] Mark as critical or full_access
* [ ] Require approval by default
* [ ] Add terminal WebSocket route
* [ ] Proxy terminal stream between frontend and agent
* [ ] Track session start/end
* [ ] Add idle timeout
* [ ] Add max session duration
* [ ] Add audit events

### Agent Checklist

* [ ] Start PTY session
* [ ] Stream PTY output
* [ ] Accept PTY input
* [ ] Enforce session timeout
* [ ] Kill PTY on disconnect
* [ ] Report session close reason

### Frontend Checklist

* [ ] Add xterm.js terminal component
* [ ] Add terminal request flow
* [ ] Add approval warning
* [ ] Add connected/disconnected state
* [ ] Add session timer
* [ ] Add close terminal button

### Acceptance Criteria

* [ ] Terminal requires approval
* [ ] Terminal opens only after approval
* [ ] Terminal disconnect cleans up PTY
* [ ] Idle timeout works
* [ ] Audit log records terminal session metadata

---

## Phase 11 — Scheduling

### Goal

Allow scheduled jobs.

### Backend Checklist

* [ ] Add scheduled_jobs table
* [ ] Add one-time schedules
* [ ] Add recurring schedules
* [ ] Add scheduler worker
* [ ] Add schedule audit events
* [ ] Apply same policy checks to scheduled jobs
* [ ] Require approval for risky schedules

### Frontend Checklist

* [ ] Add scheduled jobs page
* [ ] Add schedule creation form
* [ ] Add recurrence controls
* [ ] Show next run time
* [ ] Allow pause/resume
* [ ] Allow delete

### Acceptance Criteria

* [ ] User can schedule read/low job
* [ ] User can schedule update check
* [ ] High-risk scheduled job requires approval
* [ ] Scheduled jobs create normal job records
* [ ] Audit log records schedule creation and runs

---

## Phase 12 — Hardening and Production Readiness

### Goal

Make the system safe enough for real operations.

### Backend Checklist

* [ ] Add rate limiting
* [ ] Review CSRF protection coverage
* [ ] Add secure headers
* [ ] Add database indexes
* [ ] Add pagination
* [ ] Add log redaction
* [ ] Add backup/restore docs
* [ ] Add admin settings page
* [ ] Add token rotation
* [ ] Add agent revocation
* [ ] Add node deletion safety checks

### Agent Checklist

* [ ] Add self-update placeholder
* [ ] Add local log rotation
* [ ] Add token reload without reinstall
* [ ] Add agent health endpoint or local status command
* [ ] Add graceful shutdown
* [ ] Add better retry/backoff logic

### Frontend Checklist

* [ ] Add error boundaries
* [ ] Add loading states
* [ ] Add empty states
* [ ] Add confirmation modals
* [ ] Add keyboard-safe forms
* [ ] Add responsive layout
* [ ] Add admin settings pages

### Acceptance Criteria

* [ ] System survives agent disconnect/reconnect
* [ ] System handles backend restart
* [ ] Node status recovers after reconnect
* [ ] Large job output does not break UI
* [ ] Unauthorized users cannot access admin actions
* [ ] Agent tokens can be revoked
* [ ] Audit log is complete for sensitive actions

---

# 18. MVP Definition

The MVP is complete when the following are working end-to-end:

```text
Admin can log in
Admin can create enrollment token
Agent can enroll
Agent connects over outbound WebSocket
Node appears online
Agent sends heartbeat
Dashboard shows node health
User can run system.info
User can run service.status
User can tail journal logs
Approval engine is implemented
High-risk jobs require approval
User can restart a service
Jobs stream output live
Jobs store output history
Audit log records all sensitive activity
```

Service restart is part of the MVP only after approval workflows, policy checks, and audit logging are implemented end-to-end.

Do not add browser terminal before the MVP is stable.

Do not add arbitrary shell execution before structured jobs and approval workflows are stable.

---

# 19. Development Rules

## 19.1 Backend Rules

* Every write operation must create an audit event.
* Every job must pass through policy evaluation.
* Never dispatch jobs directly from API handlers.
* Do not trust frontend-provided risk levels.
* Risk level must come from backend action catalog.
* Validate all action parameters.
* Store job output as job events.
* Use pagination for list endpoints.
* Use typed schemas for all API requests/responses.

## 19.2 Agent Rules

* Agent must reject unknown actions.
* Agent must validate parameters locally.
* Agent must enforce timeouts.
* Agent must limit output size.
* Agent must never log secrets.
* Agent must never execute arbitrary shell unless action is `shell.run`.
* Agent must report clear success/failure.
* Agent must reconnect automatically.
* Agent should continue running if one job fails.

## 19.3 Frontend Rules

* Do not hide failed jobs.
* Do not allow dangerous actions without confirmation UI.
* Always show risk level before job submission.
* Always show approval state.
* Always show live job output.
* Use optimistic UI sparingly.
* Do not assume a job succeeded until backend confirms completion.

---

# 20. Testing Plan

## 20.1 Backend Tests

Required tests:

```text
User login
Invalid login
CSRF protection for unsafe requests
Node enrollment
Invalid enrollment token
Agent authentication
Heartbeat handling
Job creation
Policy allow
Policy deny
Approval required
Approval approve
Approval deny
Job dispatch
Job event ingestion
Job event ordering and replay
Audit creation
```

## 20.2 Agent Tests

Required tests:

```text
Config load
Enrollment payload
Heartbeat payload
Inventory collection
First-message WebSocket authentication
Unknown action rejection
system.info action
service.status action
service.restart action
logs.journal_tail action
Command timeout
Output size limit
Reconnect behavior
```

## 20.3 Frontend Tests

Required tests:

```text
Login form
Node list rendering
Node detail rendering
Job creation form
Job output viewer
Job output replay ordering
Approval card
Deny flow
Audit table
Role-based visibility
```

## 20.4 Integration Tests

Required scenarios:

```text
Agent enrolls and appears online
Agent disconnects and appears offline
User runs system.info
User restarts service
High-risk job waits for approval
Approved job dispatches
Denied job does not dispatch
Job output streams to UI
Audit log contains full trail
```

---

# 21. Operational Defaults

## 21.1 Heartbeat Interval

```text
15 seconds
```

## 21.2 Inventory Interval

```text
5 minutes
```

## 21.3 Job Timeout Defaults

```text
read actions: 60 seconds
medium actions: 120 seconds
high actions: 600 seconds
critical actions: configurable
```

## 21.4 Job Output Limit

```text
Default: 1 MB persisted output per job
Configurable later
```

When output is truncated, the final persisted output event must set `truncated` to `true`.

## 21.5 Offline Node Threshold

```text
Node is warning after 45 seconds without heartbeat
Node is offline after 90 seconds without heartbeat
```

---

# 22. Initial Seed Data

Create one default admin user from environment variables:

```text
ADMIN_USERNAME
ADMIN_EMAIL
ADMIN_PASSWORD
```

Create initial MVP-safe action catalog in code:

```text
system.info
service.list
service.status
logs.journal_tail
packages.check_updates
```

Add `service.restart`, `service.start`, and `service.stop` only after the approval engine is implemented.

Do not seed shell or terminal actions as enabled in MVP unless explicitly configured.

---

# 23. Example User Flows

## 23.1 Enroll a Node

```text
Admin logs in
Admin creates enrollment token
Admin copies install/enroll command
Agent installs on Linux box
Agent sends enrollment request
Backend creates node
Agent stores credentials
Agent connects via WebSocket
Dashboard shows node online
```

## 23.2 Restart a Service

```text
User opens node detail
User opens Services tab
User clicks Restart on nginx
Frontend submits job
Backend evaluates policy
Job is allowed
Backend dispatches job to agent
Agent runs systemctl restart nginx
Agent streams output
Backend stores events
Dashboard shows completed job
Audit log records action
```

## 23.3 High-Risk Reboot

```text
User requests reboot
Backend marks job high-risk
Job enters awaiting_approval
Admin sees approval card
Admin approves
Backend queues job
Agent receives job
Agent executes reboot command
Node disconnects
Dashboard marks node offline
Node returns online after reboot
Job is marked completed if the agent reported before reboot, or failed/expired with clear metadata if the connection dropped before completion
```

## 23.4 Denied Shell Command

```text
User requests shell.run
Backend marks critical
Approval is created
Admin denies request
Job is marked denied
Agent never receives command
Audit log records denial
```

---

# 24. Important Edge Cases

Developers must handle:

```text
Agent disconnects during job
Agent reconnects after job
Backend restarts while agents are connected
User submits job to offline node
Approval expires
Job timeout occurs
Command produces huge output
Service does not exist
Package manager lock exists
Node enrolls twice
Machine ID collision
Enrollment token expires
User loses permission after job request
Approver tries to approve own job
```

---

# 25. Non-Goals for MVP

Do not build these in the MVP:

```text
Browser terminal
Arbitrary shell commands
File editor
Multi-tenant org model
SSO
mTLS
Agent auto-update
Complex metrics charting
Full log indexing
Ansible integration
Mobile app
Plugin marketplace
```

These are later-phase features.

---

# 26. Future Enhancements

Potential later additions:

```text
SSO with Entra ID, GitHub, Google
mTLS agent authentication
Agent auto-update
Node grouping by dynamic selectors
Maintenance windows
Patch compliance dashboard
File deployment
Config drift detection
Policy-as-code
Secret broker
Session recording
Terminal transcript capture
Command templates
Webhook notifications
Telegram approval bot
Git-backed automation library
Multi-control-plane HA
```

---

# 27. Final Build Priority

Build in this order:

```text
1. Backend foundation
2. Frontend shell
3. Local auth
4. Agent enrollment
5. Agent WebSocket connection
6. Heartbeat
7. Node dashboard
8. Inventory
9. Job system
10. Safe actions
11. Job output streaming
12. Audit log
13. Approval engine
14. Service management
15. Package management
16. Bulk actions
17. Shell execution
18. Terminal
```

The project should not move to shell execution or terminal access until the job system, policy system, approval system, and audit system are stable.

---

# 28. Definition of Done

A feature is done only when:

```text
Backend endpoint exists
Database model/migration exists if needed
Frontend UI exists
Agent support exists if needed
Policy evaluation exists if action-related
Audit events exist for sensitive changes
Tests exist
Errors are handled
Documentation is updated
Manual acceptance criteria pass
```

---

# 29. Developer Notes

This project is security-sensitive. Treat every action as if it could break production infrastructure.

The primary value of the system is not that it can run commands. The value is that it can run the right command, on the right node, with the right approval, with a permanent record of who did it, why they did it, and what happened.

The first release should be boring, safe, and reliable.

Power features come later.
