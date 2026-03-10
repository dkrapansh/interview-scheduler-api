from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_recruiter, get_current_user
from app.db.session import get_db
from app.models.slot import Slot
from app.schemas.slot import SlotCreate, SlotResponse

router = APIRouter(prefix="/slots", tags=["Slots"])


@router.post("/", response_model=SlotResponse)
def create_slot(
    slot: SlotCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_recruiter)
):
    if slot.end_time <= slot.start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")

    new_slot = Slot(
        recruiter_id=current_user.id,
        start_time=slot.start_time,
        end_time=slot.end_time,
        is_booked=False
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    return new_slot


@router.get("/", response_model=list[SlotResponse])
def get_all_open_slots(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    slots = db.query(Slot).filter(Slot.is_booked == False).all()
    return slots