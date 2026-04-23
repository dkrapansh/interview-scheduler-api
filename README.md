# Interview Scheduler 

A deployed full-stack interview scheduling system where recruiters create interview slots and candidates can book, cancel, and manage interviews through a live application.

The backend is built with FastAPI and PostgreSQL, with JWT-based authentication and role-based access control. The system is designed to handle real-world scheduling constraints such as double booking prevention and consistent slot state management.

## Live System

Frontend: https://interview-scheduler-kd.netlify.app
Backend: https://interview-scheduler-api.onrender.com
API Docs: https://interview-scheduler-api.onrender.com/docs

## Overview

This project simulates a real interview scheduling workflow:
- Recruiters publish available interview slots
- Candidates discover and book slots
- Bookings are validated to prevent conflicts
- Cancelling an interview restores slot availability
The system is designed to handle concurrent booking scenarios and ensure data consistency.

## Features

- User registration with role support (recruiter, candidate)
- JWT-based authentication (stateless)
- Password hashing using Argon2
- Role-based access control for protected routes
- Recruiter-only slot creation
- Candidate-only interview booking
- Prevention of double booking using database constraints, validation, and concurrency handling
- Interview cancellation with automatic slot reopening
- Pagination and filtering for slot listing
- Structured logging for booking and cancellation events
- Deployed frontend integrated with live backend APIs
  
## Tech Stack

Backend
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
Authentication and Security
- JWT Authentication
- pwdlib / Argon2
Deployment
- Render (Backend + PostgreSQL)
- Netlify (Frontend)

## Design Highlights
### Authentication
Stateless authentication using JWT. Each request carries user identity via token, avoiding server-side session storage.
### Role-Based Access Control
- Recruiters can create slots
- Candidates can book and manage interviews
### Booking Consistency
Handles concurrent booking attempts using
- application-level checks
- database constraints
- exception handling (IntegrityError)
Ensures only one successful booking per slot.
### Slot Lifecycle
Slots move through states:
- Available → Booked → Cancelled → Available
Maintains consistent behavior across booking and cancellation flows.
### Pagination & Filtering
Supports:
- limit and offset for pagination
- optional filters(job_id, date)
Improves API usability and scalability.
### Logging
Structured logs track key actions:
- booking attempts
- cancellations
- system events
Useful for debugging and monitoring.

## Project Structure
The project follows a modular architecture separating API routes, business logic, schemas, and database models for better maintainability and scalability.
```bash
interview-scheduler-api/
│
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py            # login, JWT
│   │   ├── deps.py            # auth dependencies
│   │   ├── interview.py       # booking, cancel, summary
│   │   ├── job.py             # job APIs
│   │   ├── me.py              # current user info
│   │   ├── slot.py            # slots (filters + pagination)
│   │   └── user.py            # user registration
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging_config.py  # logging setup
│   │   └── security.py        # JWT + hashing
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── interview.py
│   │   ├── job.py
│   │   ├── slot.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── interview.py
│   │   ├── job.py
│   │   ├── slot.py
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── interview_service.py
│   │
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── styles.css
│   └── favicon.png
│
├── tests/
├── venv/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/dkrapansh/interview-scheduler-api
cd interview-scheduler-api
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create PostgreSQL database
Create a database named interview-scheduler

### 5. Add environment variables
Create a .env file and add:
```
DATABASE_URL=postgresql://postgres:whatever-password@localhost:5432/interview_scheduler
SECRET_KEY=your_secret_key_here
```

### 6. Run the Server
```bash
uvicorn app.main:app --reload
``` 
API will run at:
http://127.0.0.1:8000

Swagger docs:
http://127.0.0.1:8000/docs

## API Endpoints
### Auth
- POST /auth/login -> Login and get JWT token
### Users
- POST /users/ -> Register a new user
### Current User
- GET /me/ -> Get logged in user details
### Jobs
- POST /jobs/ — Create job (recruiter only)
- GET /jobs/ — List jobs
### Slots
- POST /slots/ -> Recruiter creates a slot
- GET /slots. -> Get all open slots [supports pagination - (limit, offset) and filtering - (job_id, date)]
### Interviews
- POST /inteviews/book -> Candidate books a slot
- GET /interviews/me -> Candidate views own interviews
- PATCH /interviews/{interview_id}/cancel -> Cancellation of interview
- GET /interviews/summary — Get today’s interview stats

## Workflow
### Recruiter flow
- 1. Register as recruiter
- 2. Login 
- 3. Create available interview slots with job name

### Candidate flow
- 1. Register as candidate
- 2. Login
- 3. View available slots
- 4. Book a slot 
- 5. Cancel interview if needed
- 6. Re-book 

## Business Rules
- Only recruiters can create slots
- Only candidates can book interviews
- A slot can only be booked once
- Cancelled interviews reopen the slot
- Users can only cancel their own interviews

## Decisions
- Used JWT instead of sessions for stateless authentication
- Enforced role-based access at API level
- Handled double booking using database constraints + exception handling
- Modeled booking as a state transition system
- Separated business logic into a service layer for clarity

## Future Improvements
- Alembic migrations
- Email notifications (booking/cancellation)
- Better slot conflict visualization
- Rate limiting
- Automated testing
- Dockerized deployment

## Why I built this?
I built this project to practice building a production style BACKEND system using FastAPI. Instead of some introductory CRUD app, I wanted to work on something that has authentication, RBAC(Role-Based Access Control), business logic and database-driven workflows that resemble a real scheduling system, while keeping the frontend simple and focused on API integration.
## Author
### Krapansh Dubey
