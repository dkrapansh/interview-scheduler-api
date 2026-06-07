from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List

class SlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    job_id: int

class SlotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recruiter_id: int
    start_time: datetime
    end_time: datetime

class SlotPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    start_time: datetime
    end_time: datetime
    job_title: str

class PaginatedSlotResponse(BaseModel):
    items: List[SlotPublic]
    total: int
    page: int
    size: int