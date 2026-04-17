from pydantic import BaseModel
class JobCreate(BaseModel):
    title: str
    description: str

class JobResponse(BaseModel):
    id: int
    title: str
    description: str
    recruiter_id: int

    class Config:
        from_attribures = True