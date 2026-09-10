from app.enrichment.dto import ProfileData
from app.qualification.icp.icp_definition import ICPDefinition
from app.qualification.llm.prompts import PromptBuilder


def test_prompt_requires_real_offer_and_recent_latest_post():
    profile = ProfileData(
        linkedin_url="https://www.linkedin.com/in/example",
        name="Jane Doe",
        headline="Business Consultant",
        about="I help B2B companies improve sales.",
        raw_text="Consulting services and audit for B2B teams.",
        latest_post_date="2026-09-09",
        latest_post_text="I am opening 3 consulting slots this week.",
    )
    icp = ICPDefinition(
        professions=["Business Consultant"],
        sectors=["Consulting"],
        target_markets=["B2B"],
        required_keywords=[],
        forbidden_keywords=[],
        minimum_confidence=0.7,
    )

    prompt = PromptBuilder().build(profile, icp)

    assert "real commercial offer" in prompt.lower()
    assert "latest_post_date" in prompt.lower()
    assert "7 days or less" in prompt
    assert "older than 7 days" in prompt
    assert "2026-09-09" in prompt


def test_prompt_does_not_invent_missing_post_date():
    profile = ProfileData(
        linkedin_url="https://www.linkedin.com/in/example",
        name="Jane Doe",
        headline="Business Consultant",
        about="",
        raw_text="Consulting services.",
    )

    prompt = PromptBuilder().build(profile)

    assert "No latest post could be identified" in prompt
    assert "do not invent or estimate a date" in prompt
