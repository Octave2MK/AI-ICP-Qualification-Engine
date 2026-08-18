import json
import uuid

from app.acquisition.acquisition_models import ICP
from app.core.logging import get_logger
from app.database.database import SessionLocal
from app.database.models import Job
from app.factory import create_full_workflow
from app.repositories.job_repository import JobRepository

logger = get_logger(__name__)

_repository = JobRepository()


def create_job(db, icp: ICP) -> Job:
    job_id = str(uuid.uuid4())
    icp_json = json.dumps(
        {
            "job_titles": icp.job_titles,
            "countries": icp.countries,
            "sectors": icp.sectors,
            "keywords": icp.keywords,
            "required_keywords": icp.required_keywords,
            "forbidden_keywords": icp.forbidden_keywords,
            "max_prospects": icp.max_prospects,
        }
    )
    return _repository.create(db, job_id, icp_json)


def get_status(db, job_id: str) -> Job | None:
    return _repository.get(db, job_id)


def get_results(db, job_id: str) -> Job | None:
    return _repository.get(db, job_id)


def run_job(job_id: str, icp: ICP) -> None:
    """Exécutée en arrière-plan (fastapi.BackgroundTasks). Ouvre sa propre
    session DB, indépendante de celle de la requête HTTP qui a créé le job
    (laquelle est déjà fermée avant que cette fonction ne s'exécute)."""
    db = SessionLocal()

    try:
        _repository.update_progress(db, job_id, 0, "Initialisation...", status="running")

        def progress_callback(percent: int, text: str) -> None:
            _repository.update_progress(db, job_id, percent, text, status="running")

        workflow = create_full_workflow(db)
        results = workflow.run(db, icp, progress_callback=progress_callback)

        serialized = [_serialize_result(item) for item in results]
        _repository.mark_succeeded(db, job_id, json.dumps(serialized))
    except Exception:
        logger.exception("Job %s failed during execution.", job_id)
        _repository.mark_failed(
            db,
            job_id,
            "Une erreur est survenue pendant le traitement. "
            "Consultez les journaux serveur pour plus de détails.",
        )
    finally:
        db.close()


def _serialize_result(item: dict) -> dict:
    """Convertit une entrée de workflow.run() (objets SQLAlchemy/dataclasses
    imbriqués) en dict JSON-safe. La forme de item["qualification"] varie
    selon le chemin emprunté par ICPQualificationPipeline._prepare():
    exclusion/pré-filtre (dict plat avec "status") ou qualification LLM
    (dict imbriqué avec "decision"/"qualification"/"score")."""
    prospect = item.get("prospect")
    name = getattr(prospect, "fullname", "") or ""
    linkedin_url = getattr(prospect, "linkedin_url", "") or ""
    job_title = getattr(prospect, "job_title", "") or ""

    qualification = item.get("qualification")
    status = None
    score = None
    confidence = None

    if isinstance(qualification, dict):
        score = qualification.get("score")

        if "status" in qualification:
            status = qualification.get("status")
        else:
            decision = qualification.get("decision")
            status = getattr(decision, "status", None)

        qual_result = qualification.get("qualification")
        if qual_result is not None:
            confidence = getattr(qual_result, "confidence", None)

    return {
        "name": name,
        "linkedin_url": linkedin_url,
        "job_title": job_title,
        "status": status,
        "score": score,
        "confidence": confidence,
        "error": item.get("error"),
    }
