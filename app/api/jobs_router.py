import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.acquisition.acquisition_models import ICP
from app.api import job_service
from app.api.dependencies import get_db
from app.api.schemas import (
    ICPRequest,
    JobCreatedResponse,
    JobResultsResponse,
    JobStatusResponse,
    ProspectResultSchema,
)

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/jobs", response_model=JobCreatedResponse, status_code=201)
def create_job(
    payload: ICPRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    icp = ICP(
        job_titles=[payload.job_title] if payload.job_title else [],
        countries=[payload.country] if payload.country else [],
        sectors=[payload.sector] if payload.sector else [],
        keywords=payload.required_keywords,
        required_keywords=payload.required_keywords,
        forbidden_keywords=payload.forbidden_keywords,
        max_prospects=payload.max_prospects,
    )

    job = job_service.create_job(db, icp)
    background_tasks.add_task(job_service.run_job, job.id, icp)

    return JobCreatedResponse(job_id=job.id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = job_service.get_status(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress_percent=job.progress_percent,
        progress_text=job.progress_text,
        error=job.error,
    )


@router.get("/jobs/{job_id}/results", response_model=JobResultsResponse)
def get_job_results(job_id: str, db: Session = Depends(get_db)):
    job = job_service.get_results(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "succeeded":
        raise HTTPException(
            status_code=409,
            detail=f"Job is not ready yet (status={job.status})",
        )

    prospects_data = json.loads(job.results_json or "[]")
    prospects = [ProspectResultSchema(**item) for item in prospects_data]

    return JobResultsResponse(job_id=job.id, prospects=prospects)
