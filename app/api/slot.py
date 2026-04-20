from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.api.deps import require_recruiter, get_current_user
from app.db.session import get_db
from app.models.slot import Slot
from app.schemas.slot import SlotCreate, SlotResponse, SlotPublic
from app.models.job import Job
from app.models.interview import Interview

router = APIRouter(prefix="/slots", tags=["Slots"])


@router.post("/", response_model=SlotResponse)
def create_slot(
    slot: SlotCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_recruiter)
):
    if slot.end_time <= slot.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    job = db.query(Job).filter(
        Job.id == slot.job_id,
        Job.recruiter_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code = 400,
            detail="Invalid job or not authorized"
        )

    new_slot = Slot(
        recruiter_id=current_user.id,
        start_time=slot.start_time,
        end_time=slot.end_time,
        job_id=slot.job_id
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    return new_slot


@router.get("/", response_model=list[SlotPublic])
def get_all_open_slots(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    slots = (
        db.query(Slot)
        .outerjoin(Interview)
        .filter(
            or_(Interview.id == None,
                Interview.status == "cancelled"
            )
        )
        .options(joinedload(Slot.job))
        .all()
    )
    return [
        {
            "id": s.id,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "job_title": s.job.title
        }
        for s in slots
    ]