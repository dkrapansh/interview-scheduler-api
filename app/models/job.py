from sqlalchemy import Column, Integer , String, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    slots = relationship("Slot", back_populates="job")