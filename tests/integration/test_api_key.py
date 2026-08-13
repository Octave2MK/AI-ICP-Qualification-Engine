import pytest

pytestmark = pytest.mark.integration

from app.core.settings import settings


def test_api_key_loaded():
    assert settings.GEMINI_API_KEY != ""