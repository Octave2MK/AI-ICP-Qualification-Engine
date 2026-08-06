from app.qualification.dto import QualificationResult
from app.scoring.ai_scoring import AIScoringEngine


def test_ai_scoring_full_match():

    qualification = QualificationResult(
        profession="Business Coach",
        sector="Consulting",
        target_market="B2B",

        offer_detected=True,

        authority_signals=[
            "Speaker"
        ],

        content_signals=[
            "LinkedIn posts"
        ],

        commercial_signals=[
            "Discovery call"
        ],

        icp_match=True,

        confidence=0.95,

        evidence=[
            "Accompagnement PME"
        ],

        exclusion_reason=None,
    )


    score, details = AIScoringEngine.calculate_score(
        qualification
    )


    assert score == 100

    assert len(details) == 5

    assert details[0]["criterion"] == "ICP Match"



def test_ai_scoring_empty_profile():

    qualification = QualificationResult(
        profession="",
        sector="",
        target_market="",

        offer_detected=False,

        authority_signals=[],

        content_signals=[],

        commercial_signals=[],

        icp_match=False,

        confidence=0.1,

        evidence=[],

        exclusion_reason="Profil non pertinent",
    )


    score, details = AIScoringEngine.calculate_score(
        qualification
    )


    assert score == 0

    assert details == []