from pydantic import BaseModel
from datetime import datetime

class InterviewCreate(BaseModel):
    slot_id: int


class InterviewResponse(BaseModel):
    id: int
    slot_id: int
    candidate_id: int
    status: str
    start_time: datetime
    end_time: datetime
    job_title: str
    
    class Config:
        from_attributes = True