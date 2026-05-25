from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.job import Job
from app.core.logging_config import logger

def create_job_service(db: Session, title: str, description: str, recruiter_id: int) -> Job:
    logger.info(f"Recruiter {recruiter_id} creating job: {title}")

    new_job = Job(
        title = title,
        description = description,
        recruiter_id = recruiter_id 
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    logger.info(f"Job created with id {new_job}")
    return new_job

def get_my_jobs_service(db: Session, recruiter_id: int) -> list[Job]:
    logger.info(f"Fetching jobs for recruiter {recruiter_id}")
    return db.query(Job).filter(Job.recruiter_id == recruiter_id).all()
