from pydantic import BaseModel, ConfigDict
from datetime import datetime

class InterviewCreate(BaseModel):
    slot_id: int

class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slot_id: int
    candidate_id: int
    candidate_email: str
    status: str
    start_time: datetime
    end_time: datetime
    job_title: str