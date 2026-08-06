from app.qualification.dto import QualificationResult
from app.qualification.decision.decision_engine import DecisionEngine


def test_decision_qualified_profile():

    result = QualificationResult(
        profession="Business Coach",
        sector="Consulting",
        target_market="B2B",

        offer_detected=True,

        authority_signals=[
            "Speaker"
        ],

        content_signals=[
            "LinkedIn creator"
        ],

        commercial_signals=[
            "Discovery call"
        ],

        icp_match=True,

        confidence=0.95,

        evidence=[
            "Accompagne des PME"
        ],

        exclusion_reason=None,
    )


    decision = DecisionEngine.decide(result)


    assert decision.status == "QUALIFIED"

    assert decision.priority == "HIGH"

    assert decision.reason == "Profil fortement compatible ICP"



def test_decision_review_profile():

    result = QualificationResult(
        profession="Consultant",
        sector="Marketing",
        target_market="B2B",

        offer_detected=True,

        authority_signals=[],

        content_signals=[],

        commercial_signals=[],

        icp_match=True,

        confidence=0.60,

        evidence=[],

        exclusion_reason=None,
    )


    decision = DecisionEngine.decide(result)


    assert decision.status == "REVIEW"

    assert decision.priority == "MEDIUM"



def test_decision_rejected_profile():

    result = QualificationResult(
        profession="Employee",
        sector="IT",
        target_market="",

        offer_detected=False,

        authority_signals=[],

        content_signals=[],

        commercial_signals=[],

        icp_match=False,

        confidence=0.80,

        evidence=[],

        exclusion_reason=None,
    )


    decision = DecisionEngine.decide(result)


    assert decision.status == "REJECTED"

    assert decision.priority == "LOW"



def test_decision_excluded_profile():

    result = QualificationResult(
        profession="Student",
        sector="Marketing",
        target_market="",

        offer_detected=False,

        authority_signals=[],

        content_signals=[],

        commercial_signals=[],

        icp_match=False,

        confidence=0.20,

        evidence=[],

        exclusion_reason="Profil étudiant",
    )


    decision = DecisionEngine.decide(result)


    assert decision.status == "EXCLUDED"

    assert decision.priority == "NONE"

    assert decision.reason == "Profil étudiant"