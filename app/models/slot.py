from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    
    job=relationship("Job", back_populates="slots")
    interviews = relationship("Interview", back_populates="slot")