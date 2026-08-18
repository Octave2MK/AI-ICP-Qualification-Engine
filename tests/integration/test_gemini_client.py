import pytest

from app.qualification.llm.gemini_client import GeminiClient

pytestmark = pytest.mark.integration


def test_gemini_client_exists():
    client = GeminiClient(
        api_key="fake-key",
        model="fake-model",
    )

    assert client._model == "fake-model"