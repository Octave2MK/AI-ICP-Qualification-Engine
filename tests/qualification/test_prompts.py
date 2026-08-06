from app.enrichment.dto import ProfileData
from app.qualification.llm.prompts import PromptBuilder


def test_build_prompt_contains_profile_information():
    profile = ProfileData(
        linkedin_url="https://linkedin.com/in/john-doe",
        name="John Doe",
        headline="Business Coach",
        about="I help companies grow.",
        raw_text="Raw profile",
        clean_text="Business coach helping SMEs improve sales."
    )

    prompt = PromptBuilder().build(profile)

    assert "John Doe" in prompt
    assert "Business Coach" in prompt
    assert "Business coach helping SMEs improve sales." in prompt

def test_prompt_is_not_empty():
    profile = ProfileData(
        linkedin_url="",
        name="",
        headline="",
        about="",
        raw_text="",
        clean_text=""
    )

    prompt = PromptBuilder().build(profile)

    assert isinstance(prompt, str)
    assert len(prompt) > 0