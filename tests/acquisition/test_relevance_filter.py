import pytest

from app.acquisition.acquisition_models import ICP, ProspectCandidate
from app.acquisition.relevance_filter import RelevanceFilter


@pytest.fixture
def relevance_filter():
    return RelevanceFilter()


@pytest.fixture
def icp():
    return ICP(
        job_titles=["Business Coach"],
        countries=["France"],
        keywords=["coaching", "entrepreneur"],
        required_keywords=["Business Coach"],
        forbidden_keywords=[
            "student",
            "étudiant",
            "intern",
            "internship",
            "stagiaire",
            "job seeker",
        ],
    )


def make_candidate(
    title: str,
    snippet: str = "",
) -> ProspectCandidate:
    return ProspectCandidate(
        url="https://www.linkedin.com/in/test-profile",
        title=title,
        snippet=snippet,
    )


def test_relevant_business_coach(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="Business Coach | Accompagnement des entrepreneurs",
        snippet="J'aide les dirigeants et entrepreneurs à développer leur activité.",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert result.passed is True
    assert result.score >= 50
    assert "Business Coach" in result.matched_titles


def test_rejects_unrelated_profession(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="Software Engineer",
        snippet="Développeur logiciel spécialisé en Python.",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert result.passed is False


def test_rejects_student(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="Business Coach Student",
        snippet="Étudiant en coaching et développement personnel.",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert result.passed is False
    assert result.matched_forbidden_keywords


def test_detects_keyword_in_title(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="Business Coach | Coaching professionnel",
        snippet="",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert "coaching" in result.matched_keywords


def test_detects_keyword_in_snippet(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="Business Coach",
        snippet="J'accompagne les entrepreneurs dans leur développement.",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert "entrepreneur" in result.matched_keywords


def test_detects_country(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="Business Coach France",
        snippet="Accompagnement des entrepreneurs.",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert result.passed is True
    assert "Country detected: France" in result.reasons


def test_is_relevant_returns_boolean(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="Business Coach",
        snippet="Accompagnement professionnel.",
    )

    result = relevance_filter.is_relevant(candidate, icp)

    assert isinstance(result, bool)
    assert result is True


def test_rejects_forbidden_keyword_even_with_high_score(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="Business Coach | Coaching entrepreneurs | France",
        snippet="Business Coach étudiant spécialisé en coaching.",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert result.passed is False
    assert result.score < 50
    assert result.matched_forbidden_keywords


def test_empty_result_is_rejected(
    relevance_filter,
    icp,
):
    candidate = make_candidate(
        title="",
        snippet="",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert result.passed is False


def test_required_keywords_are_alternatives(
    relevance_filter,
):
    icp = ICP(
        job_titles=["Coach"],
        countries=["France"],
        required_keywords=[
            "coaching",
            "consultant",
            "accompagnement",
        ],
    )

    candidate = make_candidate(
        title="Business Coach | France",
        snippet="Accompagnement des dirigeants.",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert result.passed is True
    assert result.matched_required_keywords == ["accompagnement"]


def test_required_keywords_are_actually_required(
    relevance_filter,
):
    icp = ICP(
        job_titles=["Coach"],
        countries=["France"],
        required_keywords=[
            "coaching",
            "consultant",
            "accompagnement",
        ],
    )

    candidate = make_candidate(
        title="Business Coach | France",
        snippet="J'accompagne les équipes.",
    )

    result = relevance_filter.evaluate(candidate, icp)

    assert result.passed is False
    assert result.matched_required_keywords == []
