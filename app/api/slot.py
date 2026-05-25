from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import require_recruiter, get_current_user
from app.db.session import get_db
from app.schemas.slot import SlotCreate, SlotResponse, SlotPublic
from app.services.slot_service import create_slot_service, get_open_slots_service
from app.core.logging_config import logger

router = APIRouter(prefix="/slots", tags=["Slots"])


@router.post("/", response_model=SlotResponse)
def create_slot(
    slot: SlotCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_recruiter)
):
    return create_slot_service(
        db,
        current_user.id,
        slot.job_id,
        slot.start_time,
        slot.end_time
    )


@router.get("/", response_model=list[SlotPublic])
def get_all_open_slots(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = Query(10, le=50),
    offset: int = Query(0),
    job_id: Optional[int] = Query(None),
    date: Optional[str] = Query(None)
):
    slots = get_open_slots_service(db, limit, offset, job_id, date)

    logger.info(f"Returned {len(slots)} slots for user {current_user.id}")

    return [
        {
            "id": s.id,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "job_title": s.job.title
        }
        for s in slots
    ]