from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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

    if slot.is_booked:
        raise HTTPException(status_code=400, detail="Slot is already booked")

    new_interview = Interview(
        slot_id=slot.id,
        candidate_id=current_user.id,
        status="scheduled"
    )

    slot.is_booked = True

    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)

    return new_interview


@router.get("/me", response_model=list[InterviewResponse])
def get_my_interviews(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    interviews = db.query(Interview).filter(Interview.candidate_id == current_user.id).all()
    return interviews


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

    return interview