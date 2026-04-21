from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.api.deps import require_candidate, get_current_user
from app.db.session import get_db
from app.models.interview import Interview
from app.models.slot import Slot
from app.schemas.interview import InterviewCreate, InterviewResponse
from app.services.interview_service import book_interview_service

from app.core.logging_config import logger

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("/book", response_model=InterviewResponse)
def book_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_candidate)
):
    logger.info(f"User {current_user.id} requested booking for slot {interview_data.slot_id}")

    interview, slot = book_interview_service(
        db,
        interview_data.slot_id,
        current_user
    )

    logger.info(f"Booking completed: interview_id={interview.id}, slot_id={slot.id}")

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

@router.get("/me", response_model=list[InterviewResponse])
def get_my_interviews(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    logger.info(f"Fetching interviews for user {current_user.id} (role={current_user.role})")

    if current_user.role == "candidate":
        interviews = (
            db.query(Interview)
            .options(
                joinedload(Interview.slot).joinedload(Slot.job),
                joinedload(Interview.candidate)
            )
            .filter(Interview.candidate_id == current_user.id)
            .all()
        )
    else:
        interviews = (
            db.query(Interview)
            .join(Slot, Interview.slot_id == Slot.id)
            .options(
                joinedload(Interview.slot).joinedload(Slot.job),
                joinedload(Interview.candidate)
            )
            .filter(Slot.recruiter_id == current_user.id)
            .all()
        )

    logger.info(f"Returned {len(interviews)} interviews for user {current_user.id}")

    return [
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
    logger.info(f"User {current_user.id} attempting to cancel interview {interview_id}")

    interview = (
        db.query(Interview)
        .options(joinedload(Interview.slot))
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:
        logger.warning(f"Cancel failed: interview {interview_id} not found")
        raise HTTPException(status_code=404, detail="Interview not found")

    if interview.candidate_id == current_user.id:
        pass
    elif interview.slot.recruiter_id == current_user.id:
        pass
    else:
        logger.warning(f"Unauthorized cancel attempt by user {current_user.id}")
        raise HTTPException(status_code=403, detail="Not authorized")

    if interview.status == "cancelled":
        logger.warning(f"Interview {interview_id} already cancelled")
        raise HTTPException(status_code=400, detail="Already cancelled")

    interview.status = "cancelled"
    db.commit()
    db.refresh(interview)

    logger.info(f"Interview {interview_id} cancelled by user {current_user.id}")

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
    logger.info(f"Fetching interview summary for user {current_user.id}")

    from datetime import date
    today = date.today()

    if current_user.role == "recruiter":
        interviews = (
            db.query(Interview)
            .join(Slot)
            .filter(Slot.recruiter_id == current_user.id)
            .all()
        )
    else:
        interviews = (
            db.query(Interview)
            .filter(Interview.candidate_id == current_user.id)
            .all()
        )

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