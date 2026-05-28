from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.job import JobCreate, JobResponse
from app.api.deps import require_recruiter
from app.services.job_service import create_job_service, get_my_jobs_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_recruiter)
):
    return create_job_service(db, job.title, job.description, current_user.id)


@router.get("/", response_model=list[JobResponse])
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user=Depends(require_recruiter)
):
    return get_my_jobs_service(db, current_user.id)