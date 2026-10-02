# Lead Desk

A full-stack web application for managing sales leads with secure JWT authentication and role-based access control. Users log in as either an **admin** (sees all leads and all users) or a **member** (sees and creates only their own leads). Authentication uses httpOnly cookie-based JWTs with automatic silent token refresh, refresh token rotation, and reuse detection. The entire stack runs with a single `docker compose up --build` command.

## Tech stack

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | **FastAPI** (Python 3.12) | Async-capable, built-in request validation via Pydantic, clean dependency injection for auth guards |
| ORM | **SQLAlchemy 2.0** | Mature, supports explicit queries and relationships without magic |
| Migrations | **Alembic** | First-party SQLAlchemy migration tool, runs automatically on startup |
| Database | **PostgreSQL 16** | Reliable, supports CHECK constraints and transactional DDL for safe migrations |
| Frontend | **React 19 + Vite 6 + TypeScript** | Fast dev/build tooling, type safety, widely understood component model |
| HTTP client | **Axios** | Simple interceptor API for the silent token refresh logic |
| Routing | **React Router 6** | Declarative route guards with loader/redirect support |
| Reverse proxy | **Nginx (unprivileged)** | Serves the SPA and proxies `/api` to the backend on one origin, eliminating CORS entirely |
| Containerisation | **Docker Compose** | One-command startup with service ordering, healthchecks, and named volumes |

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)

No local Python, Node.js, or PostgreSQL installation is needed.

## Getting started

```bash
cp .env.example .env
docker compose up --build
```

Wait for all three services to become healthy (the frontend starts last). This takes about 30 seconds on the first run.

## URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:3000/api (proxied through Nginx) |
| Backend direct | http://localhost:8000 (useful for debugging) |

## Seed credentials

| Email | Password | Role | Home page |
|-------|----------|------|-----------|
| admin@leaddesk.test | Admin@123 | admin | /admin |
| member@leaddesk.test | Member@123 | member | /dashboard |

Each user also has 3-4 sample leads pre-seeded.

## Running tests

```bash
docker compose run --rm backend pytest
```

This creates a separate `leaddesk_test` database, runs all tests with table truncation between each test, and never touches the main `leaddesk` database. Add `-v` for verbose output.

## Environment variables

All configuration is in `.env` (copied from `.env.example`). No secrets are committed to the repository.

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_DB` | PostgreSQL database name |
| `DATABASE_URL` | SQLAlchemy connection string used by the backend |
| `JWT_SECRET` | Secret key for signing JWT access tokens (required, no default) |
| `ACCESS_TOKEN_TTL_MINUTES` | Access token lifetime in minutes (default: 15; set to 1 to test refresh) |
| `REFRESH_TOKEN_TTL_DAYS` | Refresh token lifetime in days (default: 7) |
| `SECURE_COOKIES` | Set to `true` in production to add the Secure flag to cookies (default: false) |
| `BACKEND_PORT` | Host port mapped to the backend (default: 8000) |
| `FRONTEND_PORT` | Host port mapped to the frontend (default: 3000) |

## API endpoints

All endpoints use the `/api` prefix.

| Method | Endpoint | Access | Behaviour |
|--------|----------|--------|-----------|
| POST | /api/auth/login | Public | Validates email and password. Sets access and refresh tokens as httpOnly cookies. Returns the user object (no tokens in the body). |
| POST | /api/auth/refresh | Refresh cookie | Validates the refresh token, rotates it (old one revoked, new one issued). Reuse of a revoked token revokes all tokens for that user. |
| POST | /api/auth/logout | Logged in | Revokes the refresh token and clears both cookies. |
| GET | /api/auth/me | Logged in | Returns the current user (id, name, email, role). |
| GET | /api/leads | Logged in | Member: own leads only. Admin: all leads with the owner's name. Ordered by created_at desc. |
| POST | /api/leads | Logged in | Creates a lead owned by the current user. Validates name, email, company, website, and status. |
| GET | /api/admin/users | Admin only | Returns all users (never includes password hashes). A member gets 403. |
| GET | /api/health | Public | Returns 200 when the backend is up. Used by the Docker healthcheck. |

## Screenshots

**Login page**

![Login page](docs/screenshots/login.png)

**Member dashboard**

![Member dashboard](docs/screenshots/member_img.png)

**Admin page**

![Admin page](docs/screenshots/admin.png)

## Assumptions

- **No CORS configuration**: Nginx reverse-proxies both the frontend and the API on a single origin (`localhost:3000`), so the browser never makes a cross-origin request. No CORS headers are needed.
- **Naive UTC timestamps**: All `datetime` values are stored as PostgreSQL `timestamp without time zone` and generated with `datetime.now(timezone.utc).replace(tzinfo=None)`. This avoids timezone-aware/naive comparison issues in SQLAlchemy while keeping all times in UTC.
- **Test database uses `create_all`**: The test suite creates tables via `Base.metadata.create_all` instead of running Alembic migrations. This is simpler for test isolation but means CHECK constraints from migration `0002` are enforced by the models/DB only if SQLAlchemy declares them. The models include matching `CheckConstraint` declarations so the schemas stay in sync.
- **`email-validator` rejects `.test` TLD**: The `.test` TLD is reserved per RFC 2606 and rejected by `email-validator`. The login endpoint accepts email as a plain string (not `EmailStr`) so the seeded `@leaddesk.test` accounts work. Lead creation uses `EmailStr` as required by the spec.
- **bcrypt pinned to 4.0.1**: `passlib 1.7.4` is incompatible with `bcrypt >= 4.1` due to a removed `__about__` attribute. Pinning bcrypt avoids the breakage.

## Explanation

> To be written.
