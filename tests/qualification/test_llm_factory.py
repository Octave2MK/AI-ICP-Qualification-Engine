import types

import pytest

from app.exceptions.configuration_error import ConfigurationError
from app.qualification.llm.factory import LLMFactory
from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.gemini_client import GeminiClient

def test_create_fake_llm():
    llm = LLMFactory.create(provider="fake")

    assert isinstance(llm, FakeLLM)

@pytest.mark.integration
def test_create_gemini_llm():
    llm = LLMFactory.create(provider="gemini")

    assert isinstance(llm, GeminiClient)


def test_create_gemini_without_api_key_raises_configuration_error(monkeypatch):
    # settings is a frozen dataclass singleton, so we swap the module-level
    # reference used inside the factory rather than mutate it in place.
    fake_settings = types.SimpleNamespace(
        GEMINI_API_KEY="",
        GEMINI_MODEL="fake-model",
    )
    monkeypatch.setattr(
        "app.qualification.llm.factory.settings", fake_settings
    )

    with pytest.raises(ConfigurationError):
        LLMFactory.create(provider="gemini")