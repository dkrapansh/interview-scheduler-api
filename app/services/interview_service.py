from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.models.interview import Interview
from app.models.slot import Slot

from app.core.logging_config import logger
from app.core.middleware import get_correlation_id
from app.core.exceptions import (
    NotFoundException,
    AlreadyBookedException,
    UnauthorizedException,
    AlreadyCancelledException
)

from datetime import date
from sqlalchemy import func


def book_interview_service(db: Session, slot_id: int, user):
    logger.info(f"[{get_correlation_id()}] User {user.id} attempting to book slot {slot_id}")

    slot = (
        db.query(Slot)
        .filter(Slot.id == slot_id)
        .with_for_update()
        .first()
    )

    if not slot:
        raise NotFoundException("Slot not found")

    existing = db.query(Interview).filter(Interview.slot_id == slot_id).first()

    if existing:
        if existing.status == "scheduled":
            logger.warning(f"[{get_correlation_id()}] Slot {slot_id} is already booked.")
            raise AlreadyBookedException()

        if existing.status.lower() == "cancelled":
            existing.candidate_id = user.id
            existing.status = "scheduled"
            db.commit()
            db.refresh(existing)

            logger.info(f"[{get_correlation_id()}] Slot {slot_id} rebooked by user {user.id}")
            return existing, slot

    new_interview = Interview(
        slot_id=slot_id,
        candidate_id=user.id,
        status="scheduled"
    )

    db.add(new_interview)

    try:
        db.commit()
        db.refresh(new_interview)

        logger.info(f"[{get_correlation_id()}] Slot {slot_id} booked successfully by user {user.id}")

    except IntegrityError:
        db.rollback()
        logger.warning(f"[{get_correlation_id()}] Slot {slot_id} already booked (race condition caught by DB constraint)")
        raise AlreadyBookedException()

    return new_interview, slot


def get_my_interviews_service(db: Session, user) -> list[Interview]:
    logger.info(f"[{get_correlation_id()}] Fetching interviews for user {user.id} (role={user.role})")

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
    logger.info(f"[{get_correlation_id()}] User {user.id} attempting to cancel interview {interview_id}")

    interview = (
        db.query(Interview)
        .options(joinedload(Interview.slot))
        .filter(Interview.id == interview_id)
        .first()
    )

    if not interview:
        logger.warning(f"[{get_correlation_id()}] Cancel failed: interview {interview_id} not found")
        raise NotFoundException("Interview not found")

    if interview.candidate_id != user.id and interview.slot.recruiter_id != user.id:
        logger.warning(f"[{get_correlation_id()}] Unauthorized cancel attempt by user {user.id}")
        raise UnauthorizedException()

    if interview.status == "cancelled":
        logger.warning(f"[{get_correlation_id()}] Interview {interview_id} already cancelled")
        raise AlreadyCancelledException()

    interview.status = "cancelled"
    db.commit()
    db.refresh(interview)

    logger.info(f"[{get_correlation_id()}] Interview {interview_id} cancelled by user {user.id}")
    return interview


def get_interview_summary_service(db: Session, user) -> dict:
    logger.info(f"[{get_correlation_id()}] Fetching summary for user {user.id}")

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
        "scheduled": len([iv for iv in interviews if iv.status == "scheduled"]),
        "cancelled": len([iv for iv in interviews if iv.status == "cancelled"])
    }

    logger.info(f"[{get_correlation_id()}] Summary for user {user.id}: {summary}")
    return summary