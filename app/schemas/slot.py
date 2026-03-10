from datetime import datetime
from pydantic import BaseModel

class SlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime

class SlotResponse(BaseModel):
    id: int
    recruiter_id: int
    start_time: datetime
    end_time: datetime
    is_booked: bool

    class Config:
        from_attributes = True