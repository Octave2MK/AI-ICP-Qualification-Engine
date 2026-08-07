from sqlalchemy.orm import Session
from app.enrichment.dto import ProfileData
from app.qualification.service import QualificationService
from app.repositories.qualification_repository import QualificationRepository
from app.qualification.exclusions.exclusion_engine import ExclusionEngine


class QualificationPipeline:
    def __init__(
        self,
        qualification_service: QualificationService,
        repository: QualificationRepository,
        exclusion_engine=ExclusionEngine,
    ):
        self._qualification_service = qualification_service
        self._repository = repository
        self._exclusion_engine = exclusion_engine

    def run(
        self,
        db: Session,
        prospect_id: int,
        profile: ProfileData,
    ):

        exclusion = self._exclusion_engine.check(
            profile
        )

        if exclusion["excluded"]:
            return {
                "excluded": True,
                "reason": exclusion["reason"],
            }
        
        result = self._qualification_service.qualify(
            profile
        )

        qualification = self._repository.save(
            db,
            prospect_id,
            result,
        )
        return qualification