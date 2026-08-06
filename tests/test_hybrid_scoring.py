from app.database.models import Prospect

from app.qualification.dto import QualificationResult

from app.scoring.hybrid_scoring import HybridScoringEngine


def test_hybrid_scoring_full_profile():

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/jean",
        country="France",
        job_title="Business Coach",
        followers=5000,
    )


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
            "Coaching PME"
        ],

        exclusion_reason=None,
    )


    score, details = HybridScoringEngine.calculate_score(
        prospect,
        qualification,
    )


    # Scoring acquisition :
    # Business Coach = 25
    # France = 10
    # Followers 500-10000 = 15
    #
    # Total acquisition = 50
    #
    # Scoring IA = 100
    #
    # Score final attendu = 150

    assert score == 150

    assert len(details) == 8



def test_hybrid_scoring_without_ai_signals():

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/jean",
        country="France",
        job_title="Consultant",
        followers=100,
    )


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

        exclusion_reason="Non pertinent",
    )


    score, details = HybridScoringEngine.calculate_score(
        prospect,
        qualification,
    )


    # Consultant = 20
    # France = 10
    # Followers <500 = -5
    #
    # Score attendu = 25

    assert score == 25

    assert len(details) == 3