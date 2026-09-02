from app.core.settings import settings


def test_search_settings_exist():

    assert settings.SEARXNG_BASE_URL

    assert settings.SEARXNG_TIMEOUT > 0

    assert settings.SEARCH_RATE_LIMIT_INTERVAL > 0


def test_workflow_throttling_settings_exist():

    assert settings.WORKFLOW_COOLDOWN_SECONDS >= 0

    assert settings.MAX_WORKFLOW_RUNS_PER_SESSION > 0


def test_enrichment_engine_is_supported():

    assert settings.ENRICHMENT_ENGINE in {"bs4", "scrapy"}
