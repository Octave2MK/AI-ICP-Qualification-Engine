from types import SimpleNamespace

from app.qualification.icp.icp_definition import ICPDefinition
from app.qualification.pre_filter import ICPPreFilter


def test_required_keywords_match_when_at_least_one_keyword_is_present():
    profile = SimpleNamespace(
        name="",
        headline="Business Coach for B2B founders",
        about="",
        raw_text="",
        clean_text="",
        acquisition_title="",
        acquisition_snippet="",
    )

    icp = ICPDefinition(
        professions=["Business Coach"],
        required_keywords=[
            "coach",
            "coaching",
            "consultant",
            "formation",
            "accompagnement",
        ],
    )

    assert ICPPreFilter.match(profile, icp) is True


def test_required_keywords_reject_when_none_is_present():
    profile = SimpleNamespace(
        name="",
        headline="Software Engineer",
        about="",
        raw_text="",
        clean_text="",
        acquisition_title="",
        acquisition_snippet="",
    )

    icp = ICPDefinition(
        professions=["Business Coach"],
        required_keywords=[
            "coach",
            "coaching",
            "consultant",
            "formation",
            "accompagnement",
        ],
    )

    assert ICPPreFilter.match(profile, icp) is False