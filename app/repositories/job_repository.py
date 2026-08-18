from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database.models import Job


class JobRepository:
    """Gestion de la persistance des jobs de workflow asynchrones."""

    def create(self, db: Session, job_id: str, icp_json: str) -> Job:
        job = Job(
            id=job_id,
            status="pending",
            progress_percent=0,
            progress_text="",
            icp_json=icp_json,
            created_at=datetime.now(timezone.utc),
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        return job

    def get(self, db: Session, job_id: str) -> Job | None:
        return db.query(Job).filter(Job.id == job_id).first()

    def update_progress(
        self,
        db: Session,
        job_id: str,
        percent: int,
        text: str,
        status: str = "running",
    ) -> None:
        db.query(Job).filter(Job.id == job_id).update(
            {
                "status": status,
                "progress_percent": percent,
                "progress_text": text,
            }
        )
        db.commit()

    def mark_succeeded(self, db: Session, job_id: str, results_json: str) -> None:
        db.query(Job).filter(Job.id == job_id).update(
            {
                "status": "succeeded",
                "progress_percent": 100,
                "results_json": results_json,
                "finished_at": datetime.now(timezone.utc),
            }
        )
        db.commit()

    def mark_failed(self, db: Session, job_id: str, error: str) -> None:
        db.query(Job).filter(Job.id == job_id).update(
            {
                "status": "failed",
                "error": error,
                "finished_at": datetime.now(timezone.utc),
            }
        )
        db.commit()
