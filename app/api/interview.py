from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.api.deps import require_candidate, get_current_user
from app.db.session import get_db
from app.models.interview import Interview
from app.models.slot import Slot
from app.schemas.interview import InterviewCreate, InterviewResponse
from app.services.interview_service import book_interview_service

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("/book", response_model=InterviewResponse)
def book_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_candidate)
):
    interview, slot = book_interview_service(
        db,
        interview_data.slot_id,
        current_user
    )

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

    else:  # recruiter
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
    interview = (
        db.query(Interview)
        .options(joinedload(Interview.slot))
        .filter(Interview.id == interview_id)
        .first()
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    #  allow candidate
    if interview.candidate_id == current_user.id:
        pass
    
    # allow recruiter
    elif interview.slot.recruiter_id == current_user.id:
        pass

    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    if interview.status == "cancelled":
        raise HTTPException(status_code=400, detail="Already cancelled")

    interview.status = "cancelled"

    db.commit()
    db.refresh(interview)

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
    from datetime import datetime, date

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

    return {
        "total_today": len(today_interviews),
        "scheduled": len([iv for iv in today_interviews if iv.status == "scheduled"]),
        "cancelled": len([iv for iv in today_interviews if iv.status == "cancelled"])
    }