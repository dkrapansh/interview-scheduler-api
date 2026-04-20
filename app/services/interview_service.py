from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.interview import Interview
from app.models.slot import Slot

def book_interview_service(db: Session, slot_id: int, user):
    slot = db.query(Slot).filter(Slot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    existing = db.query(Interview).filter(Interview.slot_id == slot_id).first()
    if existing:
        if existing.status == "scheduled":
            raise HTTPException(status_code=400, detail="Slot already booked")
        
        if existing.status == "cancelled":
            existing.candidate_id = user.id
            existing.status = "scheduled"
            db.commit()
            db.refresh(existing)
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
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Slot already booked")
    
    return new_interview, slot
