from app.core.settings import settings

from app.enrichment.dto import ProfileData

from app.qualification.service import QualificationService
from app.qualification.llm.gemini_client import GeminiClient
from app.qualification.llm.prompts import PromptBuilder
from app.qualification.parsers.json_parser import JsonParser
from app.qualification.validators.result_validator import ResultValidator

import pytest
from app.qualification.exceptions import LLMError


def test_real_qualification_with_gemini():

    profile = ProfileData(
        linkedin_url="https://linkedin.com/in/john-business-coach",

        name="John Martin",

        headline="Business Coach | J'aide les PME à augmenter leurs ventes",

        about=(
            "J'accompagne les dirigeants de PME "
            "avec des programmes de coaching commercial."
        ),

        raw_text=(
            "Business coach indépendant. "
            "Créateur de contenus LinkedIn. "
            "Accompagnement premium pour entreprises."
        ),

        clean_text=(
            "Business coach indépendant. "
            "Aide les PME à améliorer leurs ventes. "
            "Programme de coaching B2B."
        ),
    )


    llm = GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
    )

    service = QualificationService(
        llm=llm,
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )


    try:
        result = service.qualify(profile)

    except LLMError as exc:
        pytest.skip(
            f"Gemini indisponible temporairement: {exc}"
        )

    assert result.profession != ""

    assert isinstance(result.icp_match, bool)

    assert 0 <= result.confidence <= 1

    assert isinstance(result.evidence, list)