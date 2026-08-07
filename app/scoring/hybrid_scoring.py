from app.scoring.scoring_engine import ScoringEngine
from app.scoring.ai_scoring import AIScoringEngine
from app.qualification.dto import QualificationResult


class HybridScoringEngine:
    @staticmethod
    def calculate_score(
        prospect,
        qualification: QualificationResult,
    ):

        acquisition_score, acquisition_details = (
            ScoringEngine.calculate_score(
                prospect
            )
        )

        ai_score, ai_details = (
            AIScoringEngine.calculate_score(
                qualification
            )
        )

        total_score = (
            acquisition_score
            +
            ai_score
        )

        details = (
            acquisition_details
            +
            ai_details
        )

        return total_score, details