from app.enrichment.dto import ProfileData

from app.qualification.exclusions.exclusion_engine import ExclusionEngine
from app.qualification.service import QualificationService
from app.qualification.decision.decision_engine import DecisionEngine

from app.scoring.hybrid_scoring import HybridScoringEngine

from app.qualification.icp.icp_definition import ICPDefinition

from app.qualification.config.icp_loader import ICPLoader

from app.qualification.pre_filter import ICPPreFilter


class ICPQualificationPipeline:

    def __init__(
        self,
        qualification_service: QualificationService,
        qualification_repository,
        icp_loader: ICPLoader,
        icp_name: str,
    ):

        self._qualification_service = qualification_service
        self._qualification_repository = qualification_repository
        self._icp = icp_loader.load(icp_name)


    def run(
        self,
        db,
        prospect,
        profile: ProfileData,
    ):


        # 1 - Vérification exclusion

        exclusion = ExclusionEngine.check(
            profile
        )


        if exclusion["excluded"]:

            return {
                "status": "EXCLUDED",
                "reason": exclusion["reason"],
                "score": 0,
            }

        # Pré-filtrage avant Gemini
        if not ICPPreFilter.match(profile):

            return {
                "status": "FILTERED",
                "decision": "REJECT",
                "score": 0,
                "reason": "Profil non pertinent pour ICP",
            }


        # 2 - Qualification IA
        cached = (
            self._qualification_repository.get_by_prospect_id(
                db,
                prospect.id,
            )
        )

        if cached:

            decision = DecisionEngine.decide(cached)

            score, details = (
                HybridScoringEngine.calculate_score(
                    prospect,
                    cached,
                )
            )

            return {
                "decision": decision,
                "qualification": cached,
                "score": score,
                "details": details,
                "cached": True,
            }


        qualification = (
            self._qualification_service.qualify(
                profile,
                self._icp,
            )
        )

        self._qualification_repository.save(
            db,
            prospect.id,
            qualification,
        )

        decision = DecisionEngine.decide(
            qualification
        )

        score, details = (
            HybridScoringEngine.calculate_score(
                prospect,
                qualification,
            )
        )

        return {
            "decision": decision,
            "qualification": qualification,
            "score": score,
            "details": details,
            "cached": False,
        }      