from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.interview import Interview
from app.models.slot import Slot

from app.core.logging_config import logger

from datetime import date
from sqlalchemy import func

def book_interview_service(db: Session, slot_id: int, user):
    logger.info(f"Unser {user.id} attempting to book slot {slot_id}")

    slot = (
        db.query(Slot)
        .filter(Slot.id == slot_id)
        .with_for_update()
        .first()
    )

    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    existing = db.query(Interview).filter(Interview.slot_id == slot_id).first()

    if existing:
        if existing.status == "scheduled":
            logger.warning(f"Slot {slot_id} is already booked.")
            raise HTTPException(status_code=400, detail="Slot already booked.")
        
        if existing.status.lower() == "cancelled":
            existing.candidate_id = user.id
            existing.status = "scheduled"
            db.commit()
            db.refresh(existing)

            logger.info(f"Slot {slot_id} rebooked by user {user.id}")
            return existing, slot
        
    new_interview = Interview(
        slot_id = slot_id,
        candidate_id = user.id,
        status = "scheduled"
    )

    db.add(new_interview)

    try:
        db.commit()
        db.refresh(new_interview)

        logger.info(f"Slot {slot_id} booked successsfully by user {user.id}")

    except IntegrityError:
        db.rollback()
        logger.warning(f"Slot {slot_id} already booked (race condition caught by DB constraint)")
        raise HTTPException(status_code=400, detail="Slot already booked")
    
    return new_interview, slot

def get_my_interviews_service(db: Session, user) -> list[Interview]:
    logger.info(f"Fetching interviews for user {user.id} (role={user.role})")

    if user.role == "candidate":
        return (
            db.query(Interview)
            .options(
                joinedload(Interview.slot).joinedload(Slot.job),
                joinedload(Interview.candidate)
            )
            .filter(Interview.candidate_id == user.id)
            .all()
        )
    else:
        return (
            db.query(Interview)
            .join(Slot, Interview.slot_id == Slot.id)
            .options(
                joinedload(Interview.slot).joinedload(Slot.job),
                joinedload(Interview.candidate)
            )
            .filter(Slot.recruiter_id == user.id)
            .all()
        )   

def cancel_interview_service(db: Session, interview_id: int, user) -> Interview:
    logger.info(f"User {user.id} attempting to cancel interview {interview_id}")

    interview = (
        db.query(Interview)
        .options(joinedload(Interview.slot))
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:
        logger.warning(f"Cancel failed: interview {interview_id} not found")
        raise HTTPException(status_code=404, detail="Interview not found")

    if interview.candidate_id != user.id and interview.slot.recruiter_id != user.id:
        logger.warning(f"Unauthorized cancel attempt by user {user.id}")
        raise HTTPException(status_code=403, detail="Not authorized")

    if interview.status == "cancelled":
        logger.warning(f"Interview {interview_id} already cancelled")
        raise HTTPException(status_code=400, detail="Already cancelled")

    interview.status = "cancelled"
    db.commit()
    db.refresh(interview)

    logger.info(f"Interview {interview_id} cancelled by user {user.id}")
    return interview

def get_interview_summary_service(db: Session, user) -> dict:
    logger.info(f"Fetching summary for user {user.id}")

    if user.role == "recruiter":
        query = (
            db.query(Interview)
            .join(Slot, Interview.slot_id == Slot.id)
            .filter(
                Slot.recruiter_id == user.id,
                func.date(Slot.start_time) == date.today()
            )
        )
    else:
        query = (
            db.query(Interview)
            .join(Slot, Interview.slot_id == Slot.id)
            .filter(
                Interview.candidate_id == user.id,
                func.date(Slot.start_time) == date.today()
            )
        )
    interviews = query.all()

    summary = {
        "total_today": len(interviews),
        "scheduled": len([iv for iv in interviews if iv.status == "scheculed"]),
        "cancelled": len([iv for iv in interviews if iv.status == "cancelled"])
    }

    logger.info(f"Summary for user {user.id}: {summary}")
    return summary