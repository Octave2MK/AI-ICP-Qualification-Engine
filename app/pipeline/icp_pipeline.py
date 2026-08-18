from app.enrichment.dto import ProfileData
from app.qualification.exclusions.exclusion_engine import ExclusionEngine
from app.qualification.service import QualificationService
from app.qualification.decision.decision_engine import DecisionEngine
from app.scoring.hybrid_scoring import HybridScoringEngine
from app.qualification.icp.icp_definition import ICPDefinition
from app.qualification.pre_filter import ICPPreFilter
from app.core.logging import get_logger

logger = get_logger(__name__)


class ICPQualificationPipeline:
    def __init__(
        self,
        qualification_service: QualificationService,
        qualification_repository,
    ):
        self._qualification_service = qualification_service
        self._qualification_repository = qualification_repository

    def run(self, db, prospect, profile: ProfileData, icp: ICPDefinition):
        prepared = self._prepare(db, prospect, profile, icp)
        if prepared is not None:
            return prepared

        qualification = self._qualification_service.qualify(profile, icp)
        return self._finalize(db, prospect, qualification, icp, cached=False)

    def run_batch(
        self,
        db,
        items: list[tuple[object, ProfileData]],
        icp: ICPDefinition,
    ) -> list[dict]:
        """Qualify all pending profiles through one LLM batch call."""
        if not items:
            return []

        results: list[dict | None] = [None] * len(items)
        pending: list[tuple[int, object, ProfileData]] = []

        for index, (prospect, profile) in enumerate(items):
            prepared = self._prepare(db, prospect, profile, icp)
            if prepared is None:
                pending.append((index, prospect, profile))
            else:
                results[index] = prepared

        if pending:
            logger.info(
                "Qualifying %d pending profile(s) via LLM batch "
                "(%d already resolved from exclusion/pre-filter/cache).",
                len(pending),
                len(items) - len(pending),
            )
            qualifications = self._qualification_service.qualify_batch(
                [profile for _, _, profile in pending],
                icp,
            )

            if len(qualifications) != len(pending):
                raise ValueError(
                    "Batch qualification count does not match pending profiles."
                )

            for (index, prospect, _profile), qualification in zip(
                pending,
                qualifications,
            ):
                results[index] = self._finalize(
                    db,
                    prospect,
                    qualification,
                    icp,
                    cached=False,
                )

        return [result for result in results if result is not None]

    def _prepare(self, db, prospect, profile, icp):
        exclusion = ExclusionEngine.check(profile)
        if exclusion["excluded"]:
            logger.info(
                "Prospect %s excluded before qualification: %s",
                getattr(prospect, "id", None),
                exclusion["reason"],
            )
            return {
                "status": "EXCLUDED",
                "reason": exclusion["reason"],
                "score": 0,
            }

        if not ICPPreFilter.match(profile, icp):
            logger.info(
                "Prospect %s filtered out by ICP pre-filter.",
                getattr(prospect, "id", None),
            )
            return {
                "status": "FILTERED",
                "decision": "REJECT",
                "score": 0,
                "reason": "Profil non pertinent pour ICP",
            }

        cached = self._qualification_repository.get_by_prospect_and_icp(
            db,
            prospect.id,
            icp.fingerprint(),
        )
        if cached:
            logger.info(
                "Qualification cache hit for prospect %s (ICP fingerprint %s).",
                getattr(prospect, "id", None),
                icp.fingerprint(),
            )
            return self._finalize(db, prospect, cached, icp, cached=True)

        return None

    def _finalize(self, db, prospect, qualification, icp, cached: bool):
        if not cached:
            self._qualification_repository.save(
                db,
                prospect.id,
                qualification,
                icp.fingerprint(),
            )

        decision = DecisionEngine.decide(
            qualification,
            minimum_confidence=icp.minimum_confidence,
        )
        score, details = HybridScoringEngine.calculate_score(
            prospect,
            qualification,
        )

        return {
            "decision": decision,
            "qualification": qualification,
            "score": score,
            "details": details,
            "cached": cached,
        }
