from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.user import User


class InterviewStatus:
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

    VALID_TRANSITIONS = {
        SCHEDULED: [CANCELLED, COMPLETED],
        CANCELLED: [],
        COMPLETED: []
    }

    @classmethod
    def can_transition(cls, from_status: str, to_status: str) -> bool:
        return to_status in cls.VALID_TRANSITIONS.get(from_status, [])

class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    slot_id = Column(Integer, ForeignKey("slots.id"), unique=True, nullable=False)
    candidate_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default=InterviewStatus.SCHEDULED)
    candidate = relationship("User")
    slot = relationship("Slot", back_populates="interviews")