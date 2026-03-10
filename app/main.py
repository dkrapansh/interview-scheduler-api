from fastapi import FastAPI
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import User, Slot, Interview
from app.api.user import router as user_router
from app.api.auth import router as auth_router
from app.api.me import router as me_router
from app.api.slot import router as slot_router
from app.api.interview import router as interview_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(me_router)
app.include_router(slot_router)
app.include_router(interview_router)


@app.get("/")
def root():
    return {"message": "Interview Scheduler API is running"}