from app.enrichment.dto import ProfileData
from app.qualification.icp.icp_definition import ICPDefinition
from app.qualification.llm.prompts import PromptBuilder


def test_prompt_uses_recency_as_a_signal_not_a_gate():
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
    assert "7 days is a strong positive activity signal" in prompt
    assert "does NOT automatically disqualify" in prompt
    assert "recency is a supporting signal, not a mandatory gate" in prompt.lower()
    assert "2026-09-09" in prompt


def test_prompt_does_not_penalize_missing_post_date():
    profile = ProfileData(
        linkedin_url="https://www.linkedin.com/in/example",
        name="Jane Doe",
        headline="Business Consultant",
        about="",
        raw_text="Consulting services.",
    )

    prompt = PromptBuilder().build(profile)

    assert "No latest post could be identified" in prompt
    assert "mark recency as unknown" in prompt.lower()
    assert "do not penalize the profile solely because the date is unavailable" in prompt.lower()
