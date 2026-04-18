from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.api.deps import require_candidate, get_current_user
from app.db.session import get_db
from app.models.interview import Interview
from app.models.slot import Slot
from app.schemas.interview import InterviewCreate, InterviewResponse

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("/book", response_model=InterviewResponse)
def book_interview(
    interview_data: InterviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_candidate)
):
    slot = db.query(Slot).filter(Slot.id == interview_data.slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")

    # Check if slot is already booked and active
    existing_interview = (
        db.query(Interview)
        .filter(Interview.slot_id == slot.id)
        .first()
    )

    if existing_interview:
        if existing_interview.status == "scheduled":
            raise HTTPException(status_code=400, detail="Slot is already booked")
        elif existing_interview.status == "cancelled":
            # Reuse cancelled interview
            existing_interview.candidate_id = current_user.id
            existing_interview.status = "scheduled"
            slot.is_booked = True
            db.commit()
            db.refresh(existing_interview)
            return {
                "id": existing_interview.id,
                "slot_id": existing_interview.slot_id,
                "candidate_id": existing_interview.candidate_id,
                "status": existing_interview.status,
                "start_time": slot.start_time,
                "end_time": slot.end_time,
                "job_title": slot.job.title
            }

    # If slot was never booked
    new_interview = Interview(
        slot_id=slot.id,
        candidate_id=current_user.id,
        status="scheduled"
    )
    slot.is_booked = True
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)
    return {
    "id": new_interview.id,
    "slot_id": new_interview.slot_id,
    "candidate_id": new_interview.candidate_id,
    "status": new_interview.status,
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
    current_user = Depends(require_candidate)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if interview.candidate_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own interview")

    if interview.status == "cancelled":
        raise HTTPException(status_code=400, detail="Interview is already cancelled")

    slot = db.query(Slot).filter(Slot.id == interview.slot_id).first()

    interview.status = "cancelled"

    if slot:
        slot.is_booked = False

    db.commit()
    db.refresh(interview)

    return {
    "id": interview.id,
    "slot_id": interview.slot_id,
    "candidate_id": interview.candidate_id,
    "status": interview.status,
    "start_time": slot.start_time if slot else None,
    "end_time": slot.end_time if slot else None,
    "job_title": slot.job.title if slot else None
}