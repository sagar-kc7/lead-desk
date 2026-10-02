Project: Lead Desk

# 1. What you will build

Build **Lead Desk**, a small full-stack web app where users log in and manage sales leads. There are two roles, admin and member, and each role sees a different part of the app.

The focus of this task is **secure authentication and role-based access**, done properly on both the backend and the frontend:

- Login with JWT access and refresh tokens stored in **httpOnly cookies**

- Automatic, silent token refresh

- Role-based access enforced on the backend, and role-based redirects on the frontend

- The whole app runs with **Docker Compose**: one command, no local setup

Keep the UI simple and clean. We care more about correct, well-structured code than about visual design.

# 2. Tech stack

| **Layer** | **Choose one**                                                           |
|-----------|--------------------------------------------------------------------------|
| Backend   | Python: FastAPI or Django (DRF allowed) · Node.js: Express or NestJS     |
| Frontend  | React (Vite) or Next.js                                                  |
| Database  | PostgreSQL, running as a Docker Compose service                          |
| Language  | TypeScript is recommended for Node.js and the frontend, but not required |

You may use any libraries you like, such as an ORM, a validation library or a UI kit. Explain your main choices in the README.

# 3. Roles and seed data

When the app starts, the database must already contain these two users (created by a seed script or migration):

| **Email**            | **Password** | **Role** | **Home page after login** |
|----------------------|--------------|----------|---------------------------|
| admin@leaddesk.test  | Admin@123    | admin    | /admin                    |
| member@leaddesk.test | Member@123   | member   | /dashboard                |

Also seed 3–5 sample leads for each user, so the tables are not empty on first run.

| **Role** | **Can do**                                                    |
|----------|---------------------------------------------------------------|
| member   | View and create **only their own** leads                      |
| admin    | View **all** leads from all users, and view the list of users |

# 4. Backend requirements

## 4.1 Data model (minimum)

| **Table**      | **Fields**                                                                                                                      |
|----------------|---------------------------------------------------------------------------------------------------------------------------------|
| users          | id, name, email (unique), password_hash, role (admin \| member), created_at                                                     |
| leads          | id, name, email, company, website (optional), status (new \| contacted \| qualified \| lost), owner_id (FK → users), created_at |
| refresh_tokens | id, user_id (FK → users), token_hash, expires_at, revoked_at (or an equivalent way to revoke tokens)                            |

Use migrations to create the schema. Do not create tables by hand.

## 4.2 API endpoints

All endpoints use the /api prefix.

| **Method** | **Endpoint**      | **Access**     | **Behaviour**                                                                                                                                                             |
|------------|-------------------|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| POST       | /api/auth/login   | Public         | Checks email and password. Sets the access and refresh tokens as httpOnly cookies. Returns the user (id, name, email, role). **Tokens must not be in the response body.** |
| POST       | /api/auth/refresh | Refresh cookie | Validates the refresh token and issues a new access token **and** a new refresh token (rotation). The old refresh token can no longer be used.                            |
| POST       | /api/auth/logout  | Logged in      | Revokes the refresh token on the server and clears both cookies.                                                                                                          |
| GET        | /api/auth/me      | Logged in      | Returns the current user and role.                                                                                                                                        |
| GET        | /api/leads        | Logged in      | member: own leads only. admin: all leads, including the owner’s name.                                                                                                     |
| POST       | /api/leads        | Logged in      | Creates a lead owned by the current user. Validates all fields.                                                                                                           |
| GET        | /api/admin/users  | admin only     | Returns all users (never password hashes). A member gets **403**.                                                                                                         |
| GET        | /api/health       | Public         | Returns 200 when the service is up. Used by the Docker healthcheck.                                                                                                       |

## 4.3 Authentication and cookie rules

- Hash passwords with **bcrypt** or **argon2**. Never store or log plain-text passwords.

- **Access token:** a JWT that lives 15 minutes and holds the user ID and role.

- **Refresh token:** lives 7 days. Store only its **hash** in the database so it can be revoked.

- Both cookies must be httpOnly and SameSite=Lax, with Secure controlled by an environment variable (off for local http, on in production).

- Limit the refresh cookie’s Path to the auth routes (for example /api/auth).

- Token lifetimes and secrets come from environment variables, for example ACCESS_TOKEN_TTL_MINUTES, REFRESH_TOKEN_TTL_DAYS and JWT_SECRET. We will set the access token to 1 minute to test your refresh logic.

- If a refresh token that has already been used is sent again, reject it.

## 4.4 Authorization, validation and errors

- Enforce roles on the **backend** for every protected endpoint. Frontend checks alone are not accepted.

- Use the correct status codes: **401** when not logged in or the token is expired or invalid, **403** when logged in with the wrong role, and **400** or **422** for invalid input.

- Validate every request body: required fields, email format, allowed status values, string lengths.

- Return errors in one consistent JSON shape, for example { "error": "message" }. Never return stack traces.

- Configure CORS for the frontend origin with credentials enabled, or serve both behind one origin with a proxy. Explain which one you chose.

## 4.5 Tests

Write at least these automated backend tests, runnable with one command inside Docker:

1.  Login with correct credentials sets both cookies. Login with a wrong password returns 401.

2.  Refresh returns new tokens, and reusing the old refresh token fails.

3.  A member calling /api/admin/users gets 403, and an admin gets 200.

4.  A member only receives their own leads from /api/leads.

# 5. Frontend requirements

## 5.1 Pages and routing

| **Route**  | **Who**          | **Content**                                                                 |
|------------|------------------|-----------------------------------------------------------------------------|
| /login     | Logged-out users | Login form. A logged-in user who opens it is redirected to their home page. |
| /dashboard | member           | The user’s own leads in a table, plus an “Add lead” form                    |
| /admin     | admin            | All leads (with an owner column) and a users table                          |
| /forbidden | Anyone           | A simple “You don’t have access” page                                       |

## 5.2 Login and role-based redirection

- The login form has client-side validation (required fields, email format), a loading state on submit, and clear error messages from the API.

- After login: an **admin** goes to /admin, a **member** goes to /dashboard.

- A logged-out user who opens any protected page is sent to /login. Bonus: return them to the page they wanted after they log in.

- A member who opens /admin goes to /forbidden (or is redirected to /dashboard).

- On page reload, restore the session by calling /api/auth/me. The user must stay logged in.

- A logout button in the header calls /api/auth/logout and sends the user to /login.

## 5.3 Token refresh logic

- The frontend **never** reads or stores tokens. No localStorage, no sessionStorage, no JS-readable cookies. The browser sends the cookies automatically.

- All API calls go through one API client (an Axios instance or a fetch wrapper) with credentials enabled.

- When a request returns **401**, the client calls /api/auth/refresh once, then retries the original request.

- If several requests fail with 401 at the same time, only **one** refresh call is made. The other requests wait for it and then retry.

- If the refresh fails, clear the user state and redirect to /login.

## 5.4 Leads UI

- Show loading, empty, error and success states for the leads table.

- The “Add lead” form validates input, shows API errors, and updates the table after a lead is created, without a full page reload.

- The layout works on desktop and mobile widths.

# 6. Docker requirements

|                                                                                                                                                                                                                                 |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **The whole project must start with one command:** docker compose up --build. We will **not** install Python, Node.js or PostgreSQL on our machine. If it does not run in Docker by following your README, we cannot review it. |

## 6.1 Compose services

| **Service** | **Requirements**                                                                                                                                       |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| db          | Official PostgreSQL image, a named volume for data, and a healthcheck (pg_isready)                                                                     |
| backend     | Built from backend/Dockerfile. Starts only after db is healthy. Runs migrations and the seed automatically on start. Has a healthcheck on /api/health. |
| frontend    | Built from frontend/Dockerfile. Starts after backend.                                                                                                  |

## 6.2 Dockerfile rules

- Each Dockerfile runs the app as a **non-root user** (USER instruction). The container must not run as root.

- Use a small, pinned base image, for example python:3.12-slim or node:22-alpine. Do not use latest.

- Order the layers so dependencies are cached: copy the dependency files and install them first, then copy the source code.

- Add a .dockerignore (exclude node_modules, .venv, .git, .env, build output).

- All configuration comes from environment variables. Commit a .env.example, never a real .env or any secrets.

- Only the ports that are needed are published to the host (frontend and backend). The database is not exposed unless you explain why.

## 6.3 Expected repository layout

> lead-desk/
>
> ├── backend/
>
> │ ├── Dockerfile
>
> │ ├── .dockerignore
>
> │ └── ... (source, migrations, seed, tests)
>
> ├── frontend/
>
> │ ├── Dockerfile
>
> │ ├── .dockerignore
>
> │ └── ... (source)
>
> ├── docker-compose.yml
>
> ├── .env.example
>
> └── README.md

# 7. Bonus (optional)

These are not required. Do them only after everything above works. A complete core task is worth more than a half-finished bonus.

- Multi-stage Dockerfiles, with a production build of the frontend served by Nginx or next start

- A single Nginx reverse proxy in Compose that serves the frontend and /api on one origin

- Next.js middleware (or a route-guard component) that protects routes before the page renders

- Admin can change a lead’s status or delete a lead; a member cannot (backend returns 403)

- Pagination, search or status filter on the leads table

- Rate limiting on /api/auth/login

- Shared TypeScript types or an OpenAPI schema between backend and frontend

- Frontend tests (for example the refresh logic or the route guards)

- A GitHub Actions workflow that runs the tests on push

- Structured request logging

# 8. Written explanation

Add a section called **“Explanation”** at the end of your README. Keep it short: **300–600 words** in total. Answer these points:

1.  **Auth flow:** what happens from login, through access-token expiry and refresh, to logout.

2.  **Refresh handling:** how your frontend avoids several refresh calls at the same time.

3.  **Role-based access:** where roles are checked on the backend, and how frontend redirects work.

4.  **Docker setup:** how the services start in order, and how you run as a non-root user.

5.  **Decisions and trade-offs:** why you chose your stack and libraries, and one thing you would do differently with more time.

6.  **What is not finished:** anything incomplete or known to be broken. Being honest here counts in your favour.

7.  **AI tools:** which AI tools you used, if any, and for what.

# 9. README requirements

Your README is the first thing we read. It must be clean and must let us run the project without asking you anything. Include:

1.  Project title and a one-paragraph summary

2.  Tech stack you chose

3.  Prerequisites (only Docker and Docker Compose)

4.  How to run: copy .env.example to .env, then docker compose up --build

5.  URLs for the frontend and the backend, and the seed login credentials

6.  How to run the tests inside Docker

7.  Environment variables, with a one-line description of each

8.  API endpoints (a short table is enough)

9.  Screenshots of the login page, member dashboard and admin page (optional but recommended)

10. The Explanation section from section 8

# 10. How to submit

1.  Push your code to a **public GitHub repository** named lead-desk (or similar).

2.  Make several commits as you work. Do not push everything in a single commit.

3.  Email your repository link to **bulanda@arrtsm.com** **before Saturday, 3 October 2026, 10:00 AM**. Use the subject “Lead Desk Task – Your Full Name”.

4.  Do not push any commits after the deadline. We review the last commit made before 10:00 AM.

If anything in this task is unclear, email your question to **bulanda@arrtsm.com**. If you need to make an assumption, write it down in your README and continue.

# 11. Review call: be ready to explain your work

If your submission passes review, we will invite you to a **15–20 minute call**. Be ready to:

- Share your screen and start the project with docker compose up --build

- Demonstrate the login, the role-based redirects and the token refresh (with a 1-minute access token)

- Explain any part of your code we point to, and why you wrote it that way

- Make a small change live, for example adding a field or a new role check

You may use AI tools while building the task, but **you must understand and be able to explain every part of your submission**. Code you cannot explain will count against you.

# 12. How we evaluate

| **Area**                             | **Points** | **What we look for**                                                                                         |
|--------------------------------------|------------|--------------------------------------------------------------------------------------------------------------|
| Authentication and security          | 25         | httpOnly cookies, refresh rotation and revocation, logout, password hashing, correct 401/403                 |
| Backend design and role-based access | 20         | Clean API structure, role checks on the backend, validation, data model, migrations                          |
| Frontend auth flow                   | 20         | Role redirects, route guards, single silent refresh, session restore on reload                               |
| Docker setup                         | 15         | One-command start, service order and healthchecks, non-root users, clean Dockerfiles, no secrets in the repo |
| Code quality                         | 10         | Readable structure, separation of concerns, consistent naming, sensible commits                              |
| README, explanation and tests        | 10         | Runs on the first try by following the README, a clear explanation, passing tests                            |
| **Total**                            | **100**    |                                                                                                              |

Bonus items can add up to 10 extra points.

## A submission will not pass if

- It does not start with docker compose up --build after following the README

- Tokens are stored in localStorage, sessionStorage or cookies readable by JavaScript

- Role checks exist only in the frontend

- Passwords are stored in plain text, or secrets are committed to the repository

- It is submitted after the deadline, or commits are pushed after the deadline

Good luck. We look forward to seeing your work.