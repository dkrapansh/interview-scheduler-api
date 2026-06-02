from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, get_db
from app.models import User, Slot, Interview, Job
from app.api.user import router as user_router
from app.api.auth import router as auth_router
from app.api.me import router as me_router
from app.api.slot import router as slot_router
from app.api.interview import router as interview_router
from app.api.job import router as job_router
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.middleware import CorrelationIDMiddleware

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins= settings.ALLOWED_ORIGINS,  # will tighten this to main URL 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationIDMiddleware)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(slot_router)
app.include_router(interview_router)
app.include_router(job_router)


@app.get("/")
def root():
    return {"message": "Interview Scheduler API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "db": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not available")    