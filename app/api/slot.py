from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_

from app.api.deps import require_recruiter, get_current_user
from app.db.session import get_db
from app.models.slot import Slot
from app.schemas.slot import SlotCreate, SlotResponse, SlotPublic
from app.models.job import Job
from app.models.interview import Interview

from typing import Optional

from app.core.logging_config import logger

router = APIRouter(prefix="/slots", tags=["Slots"])


@router.post("/", response_model=SlotResponse)
def create_slot(
    slot: SlotCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_recruiter)
):
    logger.info(f"Recruiter {current_user.id} attempting to create slot {slot.start_time} - {slot.end_time}")

    if slot.end_time <= slot.start_time:
        logger.warning("Slot creation failed: end_time <= start_time")
        raise HTTPException(status_code=400, detail="End time must be after start time")

    job = db.query(Job).filter(
        Job.id == slot.job_id,
        Job.recruiter_id == current_user.id
    ).first()

    if not job:
        logger.warning(f"Slot creation failed: invalid job_id {slot.job_id} for recruiter {current_user.id}")
        raise HTTPException(
            status_code=400,
            detail="Invalid job or not authorized"
        )

    overlap = (
        db.query(Slot)
        .filter(
            Slot.recruiter_id == current_user.id,
            and_(
                Slot.start_time < slot.end_time,
                Slot.end_time > slot.start_time
            )
        )
        .first()
    )

    if overlap:
        logger.warning(f"Slot creation failed due to overlap for recruiter {current_user.id}")
        raise HTTPException(
            status_code=400,
            detail="Slot overlaps with an existing slot"
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

    logger.info(f"Slot created successfully with id {new_slot.id} by recruiter {current_user.id}")

    return new_slot


@router.get("/", response_model=list[SlotPublic])
def get_all_open_slots(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    limit: int = Query(10, le=50),
    offset: int = Query(0),
    job_id: Optional[int] = Query(None),
    date: Optional[str] = Query(None)
):
    logger.info(f"Fetching slots | user={current_user.id} | job_id={job_id} | date={date} | limit={limit} | offset={offset}")

    query = (
        db.query(Slot)
        .outerjoin(Interview)
        .filter(
            or_(
                Interview.id == None,
                Interview.status == "cancelled"
            )
        )
        .options(joinedload(Slot.job))
    )

    if job_id:
        query = query.filter(Slot.job_id == job_id)

    if date:
        from datetime import datetime, timedelta
        try:
            target_date = datetime.fromisoformat(date).date()
            next_day = target_date + timedelta(days=1)

            query = query.filter(
                Slot.start_time >= target_date,
                Slot.start_time < next_day
            )
        except:
            logger.warning(f"Invalid date format received: {date}")
            raise HTTPException(status_code=400, detail="Invalid date format")

    slots = query.limit(limit).offset(offset).all()

    logger.info(f"Returned {len(slots)} slots")

    return [
        {
            "id": s.id,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "job_title": s.job.title
        }
        for s in slots
    ]