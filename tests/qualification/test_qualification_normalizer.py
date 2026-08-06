from app.qualification.dto import QualificationResult
from app.qualification.normalization.qualification_normalizer import (
    QualificationNormalizer,
)


def test_normalize_qualification():
    result = QualificationResult(
        profession="Coach Business",
        sector="Coaching",
        target_market="B2B",
        offer_detected=True,
        authority_signals=[],
        content_signals=[],
        commercial_signals=[],
        icp_match=True,
        confidence=0.9,
        evidence=[],
        exclusion_reason=None,
    )

    normalized = QualificationNormalizer.normalize(result)

    assert normalized.profession == "Business Coach"
    assert normalized.sector == "Consulting"