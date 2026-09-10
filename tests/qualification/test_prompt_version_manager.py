from app.qualification.prompts.prompt_version_manager import (
    PromptVersionManager,
)


def test_default_prompt_version():

    prompt = PromptVersionManager.get()

    assert prompt["name"] == "evidence_based_offer_recency_prompt"



def test_unknown_version():

    try:
        PromptVersionManager.get("v99")
        assert False

    except ValueError:
        assert True