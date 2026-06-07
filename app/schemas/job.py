from pydantic import BaseModel, ConfigDict

class JobCreate(BaseModel):
    title: str
    description: str

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    recruiter_id: int