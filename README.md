# Smart Interview Scheduler API

A backend project built with FastAPI for managing interview scheduling between recruiters and candidates.

This project allows recruiters to create interview slots and candidates to book or cancel those slots using secure JWT-based authentication.

## Features

- User registration with role support (`recruiter` and `candidate`)
- Secure login with JWT authentication
- Password hashing
- Protected routes
- Recruiter-only slot creation
- Candidate-only interview booking
- Double-booking prevention
- Interview cancellation
- Automatic reopening of slots after cancellation

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT Authentication
- pwdlib / Argon2

## Project Structure

```bash
interview-scheduler-api/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── deps.py
│   │   ├── interview.py
│   │   ├── me.py
│   │   ├── slot.py
│   │   └── user.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── interview.py
│   │   ├── slot.py
│   │   └── user.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── interview.py
│   │   ├── slot.py
│   │   └── user.py
│   │
│   └── main.py
│
├── tests/
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <my-repo-url>
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
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/interview_scheduler
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
### Slots
- POST /slots/ -> Recruiter creates a slot
- GET /slots. -> Get all open slots
### Interviews
- POST /inteviews/book -> Candidate books a slot
- GET /intervues/me -> Candidate views own interviews
- PATCH /interviews/{interview_id}/cancel -> Candidate cancels interview

## Workflow
### Recruiter flow
- 1. Register as recruiter
- 2. Login 
- 3. Create available interview slots

### Candidate flow
- 1. Register as candidate
- 2. Login
- 3. View available slots
- 4. Book a slot 
- 5. Cancel interview if needed

## Business Rules
- Only recruiters can create slots
- Only candidates can book interviews
- A slot can only be booked once
- Cancelled interviews reopen the slot
- Users can only cancel their own interviews

## Future Improvements
- Alembic migrations
- Recruiter view for booked interviews
- Slot overlap validation
- Docker support
- Automated tests
- Email notifications for booking and cancellation

## Why I built this?
I built this project to practice building a production style BACKEND system using FastAPI. Instead of some introductory CRUD app, I wanted to work on something that has authentication, RBAC(Role-Based Access Control), business logic and database-driven workflows that resemble a real scheduling system, without the added friction of frontend technologies. 

## Author
### Krapansh Dubey