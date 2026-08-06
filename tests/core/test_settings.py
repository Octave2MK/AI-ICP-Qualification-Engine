from app.core.settings import settings


def test_search_settings_exist():

    assert settings.SEARXNG_BASE_URL

    assert settings.SEARXNG_TIMEOUT > 0

    assert settings.SEARCH_RATE_LIMIT_INTERVAL > 0