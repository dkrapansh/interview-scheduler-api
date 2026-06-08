# Interview Scheduler

A deployed full-stack interview scheduling system where recruiters create interview slots and candidates can book, cancel, and manage interviews through a live application.

The backend is built with FastAPI and PostgreSQL, with JWT-based authentication and role-based access control. The system is designed to handle real-world scheduling constraints — concurrent double booking prevention, state-machine-enforced interview lifecycle, end-to-end request tracing, and background notifications.

## Live System

Frontend: https://interview-scheduler-kd.netlify.app  
Backend: https://interview-scheduler-api.onrender.com  
API Docs: https://interview-scheduler-api.onrender.com/docs

---

## Overview

This project simulates a real interview scheduling workflow:
- Recruiters publish available interview slots tied to job postings
- Candidates discover, book, and manage slots
- Bookings are validated to prevent conflicts under concurrent access
- Cancelling an interview restores slot availability for rebooking
- Every request is traceable end-to-end via correlation IDs

The system is built with production engineering depth — not just a CRUD app.

---

## Features

- User registration with role support (recruiter, candidate)
- JWT-based stateless authentication
- Password hashing using Argon2
- Role-based access control for all protected routes
- Recruiter-only slot creation with overlap detection
- Candidate-only interview booking
- 3-layer concurrent double booking prevention (SELECT FOR UPDATE + application check + DB constraint)
- Interview lifecycle modelled as a state machine (SCHEDULED → CANCELLED / COMPLETED)
- Typed custom exception hierarchy with semantic HTTP status codes
- Correlation ID middleware — UUID per request, propagated via Python contextvars, logged across all service layers
- Background email notifications on booking and cancellation (FastAPI BackgroundTasks)
- Rate limiting on login endpoint (5 requests/minute per IP via slowapi)
- Pagination and filtering on slot listing
- Structured logging with severity levels across all service operations
- Alembic database migrations with versioned upgrade/downgrade support
- 11 integration tests covering auth, RBAC, booking, cancellation, and edge cases
- /health and /ready endpoints for liveness and readiness checks
- Dockerized with Dockerfile and docker-compose for one-command local setup
- Deployed frontend integrated with live backend APIs

---

## Tech Stack

**Backend**
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic v2

**Authentication and Security**
- JWT Authentication (python-jose)
- pwdlib / Argon2
- slowapi (rate limiting)

**Testing**
- pytest
- httpx
- FastAPI TestClient

**Containerization and Deployment**
- Docker + docker-compose
- Render (Backend + PostgreSQL)
- Netlify (Frontend)

---

## Design Highlights

### Authentication
Stateless authentication using JWT. Each request carries user identity via token, avoiding server-side session storage. Token payload contains user ID, email, role, and expiry. Role is stored in both JWT (fast access) and DB (source of truth).

### Role-Based Access Control
- Recruiters can create jobs and slots
- Candidates can book and manage interviews
- Enforced via FastAPI dependency injection — `require_recruiter` and `require_candidate` in `deps.py`

### Concurrent Booking Safety
Three layers prevent double booking under simultaneous requests:
1. `SELECT FOR UPDATE` — pessimistic row lock, closes the TOCTOU window
2. Application-level check — query existing interview, return 409 if found
3. Unique DB constraint + IntegrityError catch — atomic database-level guarantee

### Interview State Machine
Interviews move through defined states with enforced transitions:
- SCHEDULED → CANCELLED
- SCHEDULED → COMPLETED
- CANCELLED and COMPLETED are terminal — nothing transitions out

Invalid transitions raise `InvalidStatusTransitionException`. Logic lives in the model — not scattered across the codebase.

### Correlation IDs
Every request gets a UUID at the middleware layer, stored in a Python `ContextVar`. Any service calls `get_correlation_id()` without it being passed as a parameter. Every log line for a request shares the same ID. Returned to clients in `X-Correlation-ID` response header.

### Service Layer
All business logic lives in `app/services/`. Route handlers are thin — they validate input, call a service, and return a response. Services are fat — they contain booking rules, state transitions, and DB operations.

### Background Notifications
Email notifications fire after booking and cancellation using FastAPI `BackgroundTasks` — the client response is not blocked. Swapping to a real SMTP/SendGrid provider is a one-function change in `notification_service.py`.

### Pagination and Filtering
`GET /slots/` returns `{items, total, page, size}`. Supports:
- `limit` and `offset` for pagination
- Optional filters: `job_id`, `date`

### Logging
Structured logs with correlation IDs track all key actions:
- Every booking attempt and completion
- Cancellation events
- Auth failures and unauthorized access attempts
- Slot creation and fetching

### Alembic Migrations
Schema changes are versioned and tracked:
- `ee10689cdbe6` — initial schema
- `998fa066b1cd` — B-tree index on `slots.recruiter_id`

Run `alembic upgrade head` to apply. Run `alembic downgrade -1` to reverse.

---

## Project Structure

```bash
interview-scheduler-api/
│
├── app/
│   ├── api/
│   │   ├── auth.py            # login, JWT, rate limited
│   │   ├── deps.py            # auth dependencies, RBAC
│   │   ├── interview.py       # booking, cancel, summary
│   │   ├── job.py             # job APIs
│   │   ├── me.py              # current user info
│   │   ├── slot.py            # slots (pagination + filters)
│   │   └── user.py            # user registration
│   │
│   ├── core/
│   │   ├── config.py          # settings, env vars
│   │   ├── exceptions.py      # typed custom exceptions
│   │   ├── limiter.py         # slowapi limiter singleton
│   │   ├── logging_config.py  # logging setup
│   │   ├── middleware.py      # correlation ID middleware
│   │   └── security.py        # JWT + password hashing
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py         # connection pool config
│   │
│   ├── models/
│   │   ├── interview.py       # Interview + InterviewStatus state machine
│   │   ├── job.py
│   │   ├── slot.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── interview.py
│   │   ├── job.py
│   │   ├── slot.py            # includes PaginatedSlotResponse
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── interview_service.py   # book, cancel, get, summary
│   │   ├── job_service.py
│   │   ├── notification_service.py # background email notifications
│   │   └── slot_service.py
│   │
│   └── main.py                # app init, middleware, routers, health endpoints
│
├── alembic/
│   └── versions/              # migration files
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
│
├── tests/
│   ├── conftest.py            # SQLite override, fixtures, helpers
│   ├── test_auth.py
│   ├── test_interviews.py
│   └── test_slots.py
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env                       # not committed
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Setup Instructions

### Option 1 — Docker (recommended, zero config)

```bash
git clone https://github.com/dkrapansh/interview-scheduler-api
cd interview-scheduler-api
docker-compose up --build
```

API runs at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

No `.env` needed — docker-compose provides local dev credentials automatically.

### Option 2 — Manual

**1. Clone the repository**
```bash
git clone https://github.com/dkrapansh/interview-scheduler-api
cd interview-scheduler-api
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1     # Windows
source venv/bin/activate        # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create PostgreSQL database**

Create a database named `interview_scheduler`

**5. Add environment variables**

Create a `.env` file:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/interview_scheduler
SECRET_KEY=your_secret_key_here
ALLOWED_ORIGINS=*
```

**6. Apply migrations**
```bash
alembic upgrade head
```

**7. Run the server**
```bash
uvicorn app.main:app --reload
```

API at `http://127.0.0.1:8000`  
Swagger docs at `http://127.0.0.1:8000/docs`

---

## Running Tests

```bash
pytest tests/ -v
```

Tests use SQLite in-memory DB via `app.dependency_overrides`. Real PostgreSQL is never touched. Rate limiter is disabled during tests via `TESTING=true` env var. Schema is reset before every test.

---

## API Endpoints

### Auth
- `POST /auth/login` → Login and get JWT token *(rate limited: 5/min)*

### Users
- `POST /users/` → Register a new user

### Current User
- `GET /me/` → Get logged-in user details

### Jobs
- `POST /jobs/` → Create a job *(recruiter only)*
- `GET /jobs/` → List own jobs *(recruiter only)*

### Slots
- `POST /slots/` → Create a slot *(recruiter only)*
- `GET /slots/` → Get all open slots *(paginated — limit, offset; filtered — job_id, date)*

### Interviews
- `POST /interviews/book` → Candidate books a slot
- `GET /interviews/me` → View own interviews
- `PATCH /interviews/{id}/cancel` → Cancel an interview
- `GET /interviews/summary` → Today's interview stats

### System
- `GET /health` → Liveness check
- `GET /ready` → Readiness check (DB connectivity)

---

## Workflow

### Recruiter flow
1. Register as recruiter
2. Login
3. Create a job posting
4. Create available interview slots linked to that job
5. View all booked interviews
6. Cancel if needed

### Candidate flow
1. Register as candidate
2. Login
3. Browse open slots
4. Book a slot
5. View booked interviews
6. Cancel if needed — slot reopens for others to book

---

## Business Rules

- Only recruiters can create jobs and slots
- Only candidates can book interviews
- A slot can only be booked by one candidate at a time
- Cancelled interviews reopen the slot for rebooking
- Users can only cancel interviews they are part of (as candidate or recruiter)
- Interview status transitions are strictly enforced — CANCELLED and COMPLETED are terminal
- Login is rate limited to 5 attempts per minute per IP

---

## Design Decisions

- JWT over sessions — stateless auth, no server-side session storage, scales horizontally
- SELECT FOR UPDATE over optimistic locking — higher contention expected on slot booking; pessimistic lock eliminates the TOCTOU window cleanly
- State machine over boolean flag — extensible, self-documenting, transition rules enforced at the model level
- ContextVar over parameter passing — keeps service function signatures clean while making correlation IDs available everywhere in the request lifecycle
- BackgroundTasks over Celery — no retry or persistence needed at this scale; one-function swap to upgrade
- Alembic over create_all() — production databases need versioned, reversible schema changes
- Docker for reproducible local setup — eliminates environment inconsistencies, matches production packaging

---

## Why I built this

I built this to practice building a production-style backend system with FastAPI. Instead of a basic CRUD app, I wanted something with real engineering problems baked in — authentication, RBAC, concurrent booking, state management, observability, and schema evolution. Every feature maps to a concept that appears in production systems, and every decision has a reason I can defend.

---

## Author

Krapansh Dubey · [LinkedIn](https://linkedin.com/in/dkrapansh) · [GitHub](https://github.com/dkrapansh)
