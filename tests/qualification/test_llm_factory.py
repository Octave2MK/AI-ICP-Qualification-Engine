from app.qualification.llm.factory import LLMFactory
from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.gemini_client import GeminiClient


def test_create_fake_llm():
    llm = LLMFactory.create(provider="fake")

    assert isinstance(llm, FakeLLM)


def test_create_gemini_llm():
    llm = LLMFactory.create(provider="gemini")

    assert isinstance(llm, GeminiClient)