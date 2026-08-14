from app.qualification.dto import QualificationResult
from app.qualification.decision.dto import ICPDecision


class DecisionEngine:
    @staticmethod
    def decide(
        result: QualificationResult,
        minimum_confidence: float = 0.85,
    ) -> ICPDecision:

        if not 0.0 <= minimum_confidence <= 1.0:
            raise ValueError(
                "minimum_confidence must be between 0.0 and 1.0"
            )

        if result.exclusion_reason:
            return ICPDecision(
                status="EXCLUDED",
                reason=result.exclusion_reason,
                priority="NONE",
            )

        if not result.icp_match:
            return ICPDecision(
                status="REJECTED",
                reason="Profil hors ICP",
                priority="LOW",
            )

        if result.confidence >= minimum_confidence:
            return ICPDecision(
                status="QUALIFIED",
                reason="Profil fortement compatible ICP",
                priority="HIGH",
            )

        return ICPDecision(
            status="REVIEW",
            reason="Qualification incertaine",
            priority="MEDIUM",
        )
