from app.enrichment.dto import ProfileData
from app.qualification.exclusions.exclusion_engine import ExclusionEngine
from app.qualification.service import QualificationService
from app.qualification.decision.decision_engine import DecisionEngine
from app.scoring.hybrid_scoring import HybridScoringEngine
from app.qualification.icp.icp_definition import ICPDefinition
from app.qualification.pre_filter import ICPPreFilter


class ICPQualificationPipeline:
    def __init__(
        self,
        qualification_service: QualificationService,
        qualification_repository,
    ):
        self._qualification_service = qualification_service
        self._qualification_repository = qualification_repository

    def run(
        self,
        db,
        prospect,
        profile: ProfileData,
        icp: ICPDefinition,
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

        # 2 - Pré-filtrage avant Gemini
        if not ICPPreFilter.match(
            profile,
            icp,
        ):
            return {
                "status": "FILTERED",
                "decision": "REJECT",
                "score": 0,
                "reason": "Profil non pertinent pour ICP",
            }

        # 3 - Cache strictement lié à l'ICP courant.
        # Un même prospect peut être qualifié pour plusieurs ICP différents.
        icp_fingerprint = icp.fingerprint()
        cached = (
            self._qualification_repository.get_by_prospect_and_icp(
                db,
                prospect.id,
                icp_fingerprint,
            )
        )

        if cached:
            decision = DecisionEngine.decide(
                cached
            )

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

        # 4 - Qualification IA selon l'ICP dynamique
        qualification = (
            self._qualification_service.qualify(
                profile,
                icp,
            )
        )

        # 5 - Persistance avec l'identifiant de l'ICP courant
        self._qualification_repository.save(
            db,
            prospect.id,
            qualification,
            icp_fingerprint,
        )

        # 6 - Décision
        decision = DecisionEngine.decide(
            qualification
        )

        # 7 - Score hybride
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
