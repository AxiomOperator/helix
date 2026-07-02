# Linux Command Center

Linux Command Center is a custom Linux fleet management command center. Phase 0 provides only the base repository, local development environment, and skeleton services that later phases will build on.

No authentication, node enrollment, agent WebSocket communication, job execution, approvals, metrics collection, or terminal functionality is implemented in this phase.

## Stack

* Backend: FastAPI, Python 3.12, SQLAlchemy 2.x, Alembic, PostgreSQL, Pydantic Settings, structured logging
* Frontend: Next.js, TypeScript, App Router, TailwindCSS, ShadCN-ready configuration
* Agent: Go CLI with config loader and version command
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
