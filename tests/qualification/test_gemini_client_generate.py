from types import SimpleNamespace

import pytest

from app.qualification.exceptions import LLMError
from app.qualification.llm.gemini_client import GeminiClient


def _make_client():
    # Construction only needs a non-empty key; no network call happens here.
    return GeminiClient(api_key="fake-key", model="fake-model")


def test_generate_returns_response_text(monkeypatch):
    client = _make_client()
    monkeypatch.setattr(
        client._client.models,
        "generate_content",
        lambda model, contents: SimpleNamespace(text="hello"),
    )

    assert client._generate("prompt") == "hello"


def test_generate_raises_llm_error_when_response_text_is_none(monkeypatch):
    """Gemini can return a response with no text (e.g. safety-filtered
    output); this must surface as a clear LLMError, not a silent None
    propagating into JSON parsing downstream."""
    client = _make_client()
    monkeypatch.setattr(
        client._client.models,
        "generate_content",
        lambda model, contents: SimpleNamespace(text=None),
    )

    with pytest.raises(LLMError, match="empty response"):
        client._generate("prompt")


def test_generate_wraps_non_rate_limit_errors_in_llm_error(monkeypatch):
    client = _make_client()

    def raise_error(model, contents):
        raise RuntimeError("boom")

    monkeypatch.setattr(client._client.models, "generate_content", raise_error)

    with pytest.raises(LLMError, match="boom"):
        client._generate("prompt")
