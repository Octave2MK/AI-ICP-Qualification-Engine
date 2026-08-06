from app.qualification.dto import QualificationResult
from app.qualification.decision.dto import ICPDecision


class DecisionEngine:

    @staticmethod
    def decide(
        result: QualificationResult
    ) -> ICPDecision:


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


        if result.confidence >= 0.85:

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