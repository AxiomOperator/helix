# Linux Command Center

Linux Command Center is a custom Linux fleet management command center. The current implementation includes the local development stack, cookie-based local auth, base dashboard UI, node enrollment, and initial outbound agent WebSocket connectivity.

Job execution, approvals, metrics collection, service management, package management, and terminal functionality are not implemented yet.

## Stack

* Backend: FastAPI, Python 3.12, SQLAlchemy 2.x, Alembic, PostgreSQL, Pydantic Settings, structured logging
* Frontend: Next.js, TypeScript, App Router, TailwindCSS, ShadCN-ready configuration
* Agent: Go CLI with config loader, enrollment, and outbound WebSocket connection
* DevOps: Docker Compose with backend, frontend, PostgreSQL, and Redis

## Local Requirements

* Docker and Docker Compose
* Go 1.22 or newer for local agent builds
* Python 3.12 or newer for local backend development outside Docker
* Node.js 20 or newer for local frontend development outside Docker

## Start With Docker Compose

```bash
docker compose up --build
```

Backend: `http://localhost:8000`

Frontend: `http://localhost:3000`

PostgreSQL: `localhost:5432`

Redis: `localhost:6379`

## Verify Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "linux-command-center-backend"
}
```

## Phase 1 Local Auth

The backend seeds a local admin user from environment variables when it starts:

```text
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me-now
ADMIN_DISPLAY_NAME=Administrator
```

Use `admin` / `change-me-now` at `http://localhost:3000/login` in local development.

The backend uses an HttpOnly `lcc_session` cookie and requires `X-CSRF-Token` on unsafe authenticated requests such as logout.

## Phase 2 Node Enrollment

Admins can create one-time enrollment tokens from `http://localhost:3000/dashboard/nodes`.

After building the agent, enroll a host with the token shown in the dashboard:

```bash
cd agent
./command-agent enroll --server-url http://localhost:8000 --token <enrollment-token>
./command-agent connect
```

For local testing without writing `/etc/linux-command-agent/config.toml`, pass a temporary config path:

```bash
./command-agent enroll --server-url http://localhost:8000 --token <enrollment-token> --config /tmp/helix-agent.toml
./command-agent connect --config /tmp/helix-agent.toml
```

Enrollment tokens and agent tokens are stored only as hashes in PostgreSQL. The WebSocket requires `agent.auth` as the first message before any other agent message is accepted.

## Access Frontend

Open `http://localhost:3000`.

The home page should show:

```text
Linux Command Center
Custom Linux fleet management dashboard
```

## Build The Go Agent

```bash
cd agent
go build -o command-agent ./cmd/command-agent
./command-agent version
```

Expected output:

```text
linux-command-agent 0.1.0
```

## Phase 0 Acceptance Criteria

* [x] Repository structure exists
* [x] FastAPI backend starts
* [x] Backend config loader works
* [x] PostgreSQL connection scaffolding exists
* [x] SQLAlchemy base/session exists
* [x] Alembic scaffolding exists
* [x] `/health` returns OK
* [x] Structured logging exists
* [x] Root `.env.example` exists
* [x] Next.js TypeScript frontend starts
* [x] App Router routes exist
* [x] API client helper exists
* [x] Base layout exists
* [x] Login placeholder page exists
* [x] Dashboard placeholder page exists
* [x] Go agent module exists
* [x] Agent config loader exists
* [x] Agent CLI exists
* [x] Agent version command works
* [x] Systemd unit template exists
* [x] Install script placeholder exists
* [x] Docker Compose starts backend, frontend, Postgres, and Redis
* [x] Backend health endpoint returns OK through Docker
* [x] Frontend loads in browser through Docker
* [x] Agent binary builds locally
