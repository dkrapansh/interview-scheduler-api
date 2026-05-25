from datetime import datetime
from pydantic import BaseModel
from typing import List

class SlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    job_id: int

class SlotResponse(BaseModel):
    id: int
    recruiter_id: int
    start_time: datetime
    end_time: datetime

    class Config:
        from_attributes = True

class SlotPublic(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    job_title: str

    class Config:
        from_attributes = True

class PaginatedSlotResponse(BaseModel):
    items: List[SlotPublic]
    total: int
    page: int
    size: int