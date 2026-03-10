from pydantic import BaseModel


class InterviewCreate(BaseModel):
    slot_id: int


class InterviewResponse(BaseModel):
    id: int
    slot_id: int
    candidate_id: int
    status: str

    class Config:
        from_attributes = True