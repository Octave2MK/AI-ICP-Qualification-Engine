from app.enrichment.dto import ProfileData
from app.qualification.icp.icp_definition import ICPDefinition
from app.qualification.llm.prompts import PromptBuilder


def test_prompt_contains_icp():

    profile = ProfileData(
        linkedin_url="",
        name="Jean",
        headline="Business Coach",
        about="",
        raw_text="",
        clean_text="Business coaching B2B",
    )

    icp = ICPDefinition(
        professions=[
            "Business Coach"
        ],
        sectors=[
            "Consulting"
        ],
        target_markets=[
            "B2B"
        ],
        required_keywords=[
            "coaching"
        ],
    )


    prompt = PromptBuilder().build(
        profile,
        icp,
    )


    assert "Business Coach" in prompt
    assert "Consulting" in prompt
    assert "B2B" in prompt