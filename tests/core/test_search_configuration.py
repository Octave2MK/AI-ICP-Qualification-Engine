from app.core.settings import settings


def test_retry_configuration_exists():

    assert settings.SEARCH_RETRY_ATTEMPTS >= 1

    assert settings.SEARCH_RETRY_DELAY >= 0