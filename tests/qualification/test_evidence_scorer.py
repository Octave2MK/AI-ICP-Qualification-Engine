from app.qualification.evidence.evidence_scorer import EvidenceScorer


def test_high_confidence_evidence():
    evidence = [
        "Headline mentions Business Coach",
        "About mentions coaching",
        "Targets SMEs",
    ]

    score = EvidenceScorer.score(evidence)

    assert score >= 0.8


def test_low_confidence_evidence():
    evidence = [
        "One keyword only",
    ]

    score = EvidenceScorer.score(evidence)

    assert score < 0.5