import pytest

from app.qualification.dto import QualificationResult
from app.qualification.decision.decision_engine import DecisionEngine


def _make_result(**overrides) -> QualificationResult:
    defaults = dict(
        profession="Business Coach",
        sector="Consulting",
        target_market="B2B",
        offer_detected=True,
        authority_signals=[],
        content_signals=[],
        commercial_signals=[],
        icp_match=True,
        confidence=0.95,
        evidence=["Accompagne des PME"],
        exclusion_reason=None,
    )
    defaults.update(overrides)
    return QualificationResult(**defaults)


@pytest.mark.parametrize(
    "overrides, expected_status, expected_priority",
    [
        pytest.param(
            dict(icp_match=True, confidence=0.95, evidence=["Accompagne des PME"]),
            "QUALIFIED",
            "HIGH",
            id="qualified",
        ),
        pytest.param(
            dict(icp_match=True, confidence=0.60, evidence=[]),
            "REVIEW",
            "MEDIUM",
            id="review",
        ),
        pytest.param(
            dict(icp_match=False, confidence=0.80, evidence=[]),
            "REJECTED",
            "LOW",
            id="rejected",
        ),
        pytest.param(
            dict(
                icp_match=False,
                confidence=0.20,
                evidence=[],
                exclusion_reason="Profil étudiant",
            ),
            "EXCLUDED",
            "NONE",
            id="excluded",
        ),
    ],
)
def test_decision_status_and_priority(overrides, expected_status, expected_priority):
    result = _make_result(**overrides)

    decision = DecisionEngine.decide(result)

    assert decision.status == expected_status
    assert decision.priority == expected_priority


def test_decision_excluded_reason_is_propagated():
    result = _make_result(
        icp_match=False,
        confidence=0.20,
        evidence=[],
        exclusion_reason="Profil étudiant",
    )

    decision = DecisionEngine.decide(result)

    assert decision.reason == "Profil étudiant"


def test_decision_qualified_reason():
    result = _make_result(icp_match=True, confidence=0.95)

    decision = DecisionEngine.decide(result)

    assert decision.reason == "Profil fortement compatible ICP"


def test_decision_at_exact_minimum_confidence_boundary_is_qualified():
    """confidence == minimum_confidence is inclusive (>=), so it must be
    treated as QUALIFIED rather than falling into REVIEW."""
    result = _make_result(icp_match=True, confidence=0.85)

    decision = DecisionEngine.decide(result, minimum_confidence=0.85)

    assert decision.status == "QUALIFIED"


def test_decision_just_below_minimum_confidence_boundary_is_review():
    result = _make_result(icp_match=True, confidence=0.849999)

    decision = DecisionEngine.decide(result, minimum_confidence=0.85)

    assert decision.status == "REVIEW"


@pytest.mark.parametrize("invalid_minimum_confidence", [-0.01, 1.01, 2.0, -5.0])
def test_decide_rejects_minimum_confidence_out_of_range(invalid_minimum_confidence):
    result = _make_result()

    with pytest.raises(ValueError):
        DecisionEngine.decide(
            result, minimum_confidence=invalid_minimum_confidence
        )


@pytest.mark.parametrize("boundary_minimum_confidence", [0.0, 1.0])
def test_decide_accepts_minimum_confidence_at_valid_boundaries(
    boundary_minimum_confidence,
):
    result = _make_result()

    # Should not raise.
    DecisionEngine.decide(result, minimum_confidence=boundary_minimum_confidence)
