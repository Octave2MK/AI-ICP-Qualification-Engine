from app.qualification.dto import QualificationResult


def test_qualification_result_defaults():
    result = QualificationResult(
        profession="Coach",
        sector="Business",
        target_market="B2B",
        offer_detected=True,
    )

    assert result.profession == "Coach"
    assert result.sector == "Business"
    assert result.target_market == "B2B"

    assert result.authority_signals == []
    assert result.content_signals == []
    assert result.commercial_signals == []

    assert result.icp_match is False
    assert result.confidence == 0.0
    assert result.evidence == []
    assert result.exclusion_reason is None