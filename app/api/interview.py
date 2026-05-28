from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_candidate, get_current_user
from app.db.session import get_db
from app.schemas.interview import InterviewCreate, InterviewResponse
from app.services.interview_service import (
    book_interview_service,
    get_my_interviews_service,
    cancel_interview_service
)
from app.core.logging_config import logger

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("/book", response_model=InterviewResponse, status_code=201)
def book_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_candidate)
):
    logger.info(f"User {current_user.id} requested booking for slot {interview_data.slot_id}")

    interview, slot = book_interview_service(db, interview_data.slot_id, current_user)
    return {
        "id": interview.id,
        "slot_id": interview.slot_id,
        "candidate_id": interview.candidate_id,
        "candidate_email": current_user.email,
        "status": interview.status,
        "start_time": slot.start_time,
        "end_time": slot.end_time,
        "job_title": slot.job.title
    }

@router.get("/me", response_model=InterviewResponse)
def get_my_interviews(
    db: Session = Depends(get_db),
    current_user = get_current_user
):
    interviews = get_my_interviews_service(db, current_user)

    return[
        {
            "id": iv.id,
            "slot_id": iv.slot_id,
            "candidate_id": iv.candidate_id,
            "candidate_email": iv.candidate.email,
            "status": iv.status,
            "start_time": iv.slot.start_time,
            "end_time": iv.slot.end_time,
            "job_title": iv.slot.job.title           
        }
        for iv in interviews
    ]

@router.patch("/{interview_id}/cancel", response_model=InterviewResponse)
def cancel_interview(
    interview_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    interview = cancel_interview_service(db, interview_id, current_user)

    return {
        "id": interview.id,
        "slot_id": interview.slot_id,
        "candidate_id": interview.candidate_id,
        "candidate_email": interview.candidate.email,
        "status": interview.status,
        "start_time": interview.slot.start_time,
        "end_time": interview.slot.end_time,
        "job_title": interview.slot.job.title
    }

@router.get("/summary")
def get_interview_summary(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from datetime import date
    today = date.today()

    interviews = get_my_interviews_service(db, current_user)

    today_interviews = [
        iv for iv in interviews
        if iv.slot.start_time.date() == today
    ]

    summary = {
        "total_today": len(today_interviews),
        "scheduled": len([iv for iv in today_interviews if iv.status == "scheduled"]),
        "cancelled": len([iv for iv in today_interviews if iv.status == "cancelled"])
    }

    logger.info(f"Summary for user {current_user.id}: {summary}")

    return summary