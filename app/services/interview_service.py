from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.interview import Interview
from app.models.slot import Slot

from app.core.logging_config import logger 


def book_interview_service(db: Session, slot_id: int, user):
    
    logger.info(f"User {user.id} attempting to book slot {slot_id}")

    slot = db.query(Slot).filter(Slot.id == slot_id).with_for_update().first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    existing = db.query(Interview).filter(Interview.slot_id == slot_id).first()

    if existing:
        if existing.status == "scheduled":
            logger.warning(f"Slot {slot_id} already booked")
            raise HTTPException(status_code=400, detail="Slot already booked")
        
        if existing.status.lower() == "cancelled":
            existing.candidate_id = user.id
            existing.status = "scheduled"
            db.commit()
            db.refresh(existing)

            logger.info(f"Slot {slot_id} rebooked by user {user.id}")

            return existing, slot

    new_interview = Interview(
        slot_id = slot.id,
        candidate_id = user.id,
        status = "scheduled"
    )

    db.add(new_interview)

    try:
        db.commit()
        db.refresh(new_interview)

        logger.info(f"Slot {slot_id} booked successfully by user {user.id}")

    except IntegrityError:
        db.rollback()
        logger.warning(f"Slot {slot_id} already booked (race condition)")
        raise HTTPException(status_code=400, detail="Slot already booked")
    
    return new_interview, slot