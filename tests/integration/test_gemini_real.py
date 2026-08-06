import pytest

pytestmark = pytest.mark.integration
from app.core.settings import settings
from app.qualification.llm.gemini_client import GeminiClient


def test_gemini_real():
    client = GeminiClient(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
    )

    response = client.analyze(
        "Reply with exactly the single word: Hello"
    )

    assert isinstance(response, str)
    assert len(response.strip()) > 0