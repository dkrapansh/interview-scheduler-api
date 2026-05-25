from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from fastapi import HTTPException
from datetime import datetime, timedelta
from typing import Optional

from app.models.slot import Slot
from app.models.job import Job
from app.models.interview import Interview
from app.core.logging_config import logger

def create_slot_service(
        db: Session,
        recruiter_id: int,
        job_id: int,
        start_time: datetime, 
        end_time: datetime
) -> Slot: 
    logger.info(f"Recruiter {recruiter_id} creating slot {start_time} - {end_time}")

    if end_time <= start_time:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == recruiter_id
    ).first()

    if not job:
        raise HTTPException(status_code=400, detail="Invalid job or not authorized")
    
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
        raise HTTPException(status_code=400, detail="Slot overlaps with an existing slot.")
    
    new_slot = Slot(
        recruiter_id = recruiter_id,
        start_time = start_time,
        end_time = end_time,
        job_id = job_id
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    logger.info(f"Slot created with id {new_slot.id}")
    return new_slot

def get_open_slots_service(
        db: Session,
        limit: int,
        offset: int,
        job_id: Optional[int],
        date: Optional[str]
) -> list[Slot]:
    logger.info(f"Fetching open slots | job_id = {job_id} | date = {date}")

    query = (
        db.query(Slot)
        .outerjoin(Interview)
        .filter(
            or_(Interview.id == None,
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
            raise HTTPException(status_code=400, detail="Invalid date format.")
    
    return query.limit(limit).offset(offset).all()