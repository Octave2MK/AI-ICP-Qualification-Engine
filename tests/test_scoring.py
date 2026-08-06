from app.database.models import Prospect
from app.scoring.scoring_engine import ScoringEngine


def test_business_coach():

    prospect = Prospect(
        fullname="Jean",
        job_title="Coach Business",
        country="France",
        followers=3500
    )

    score, _ = ScoringEngine.calculate_score(prospect)

    assert score == 50


def test_unknown_profile():

    prospect = Prospect(
        fullname="Paul",
        job_title="Étudiant",
        country="Togo",
        followers=120
    )

    score, _ = ScoringEngine.calculate_score(prospect)

    assert score == -5


def test_consultant():

    prospect = Prospect(
        fullname="Marie",
        job_title="Consultant Marketing",
        country="Belgique",
        followers=8000
    )

    score, _ = ScoringEngine.calculate_score(prospect)

    assert score == 43