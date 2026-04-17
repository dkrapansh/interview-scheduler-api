from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse
from app.api.deps import require_recruiter

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(require_recruiter)
):
    new_job = Job(
        title=job.title,
        description=job.description,
        recruiter_id=current_user.id
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job

@router.get("/", response_model=list[JobResponse])
def get_my_jobs(
    db: Session = Depends(get_db), 
    current_user = Depends(require_recruiter)
):
    jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
    return jobs
