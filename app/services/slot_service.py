from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Optional

from app.models.slot import Slot
from app.models.job import Job
from app.models.interview import Interview
from app.core.logging_config import logger
from app.core.middleware import get_correlation_id
from app.core.exceptions import (
    InvalidSlotTimeException,
    NotFoundException,
    SlotOverlapException
)


def create_slot_service(
        db: Session,
        recruiter_id: int,
        job_id: int,
        start_time: datetime,
        end_time: datetime
) -> Slot:
    logger.info(f"[{get_correlation_id()}] Recruiter {recruiter_id} creating slot {start_time} - {end_time}")

    if end_time <= start_time:
        raise InvalidSlotTimeException()

    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == recruiter_id
    ).first()

    if not job:
        raise NotFoundException("Invalid job or not authorized")

    overlap = (
        db.query(Slot)
        .filter(
            Slot.recruiter_id == recruiter_id,
            and_(
                Slot.start_time < end_time,
                Slot.end_time > start_time
            )
        )
        .first()
    )

    if overlap:
        raise SlotOverlapException()

    new_slot = Slot(
        recruiter_id=recruiter_id,
        start_time=start_time,
        end_time=end_time,
        job_id=job_id
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    logger.info(f"[{get_correlation_id()}] Slot created with id {new_slot.id}")
    return new_slot


def get_open_slots_service(
    db: Session,
    limit: int,
    offset: int,
    job_id: Optional[int],
    date: Optional[str]
) -> dict:
    logger.info(f"[{get_correlation_id()}] Fetching open slots | job_id={job_id} | date={date}")

    query = (
    db.query(Slot)
    .join(Job, Slot.job_id == Job.id)
    .outerjoin(Interview, Interview.slot_id == Slot.id)
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
        try:
            target_date = datetime.fromisoformat(date).date()
            next_day = target_date + timedelta(days=1)
            query = query.filter(
                Slot.start_time >= target_date,
                Slot.start_time < next_day
            )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date format")

    total = query.count()
    slots = query.limit(limit).offset(offset).all()

    page = (offset // limit) + 1

    return {
        "items": slots,
        "total": total,
        "page": page,
        "size": limit
    }