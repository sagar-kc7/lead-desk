# Lead Desk
Spec: docs/task.md (source of truth; re-read it before finishing each phase).

## Stack
FastAPI, SQLAlchemy, Alembic, PostgreSQL, pytest | React + Vite + TS, React Router, Axios | Docker Compose, Nginx (unprivileged) proxying /api.

## Non-negotiables
- Tokens ONLY in httpOnly, SameSite=Lax cookies; never in response bodies; frontend never touches them.
- Secure flag, token TTLs and secrets come from env vars. Commit .env.example only.
- Refresh rotation: store only the SHA-256 hash of the refresh token; reject reuse; revoke on logout.
- Refresh cookie Path=/api/auth.
- Roles enforced in backend dependencies on every protected route (401 vs 403 vs 422).
- Consistent errors: {"error": "message"}; no stack traces.
- All Dockerfiles: pinned base image, non-root USER, deps layer cached, .dockerignore.
- Everything runs via `docker compose up --build`; migrations + idempotent seed run on backend start.

## Workflow
Work in small steps, tell me what you changed and why, keep code simple enough for me to explain line by line. Don't add features beyond the spec until the core passes.
