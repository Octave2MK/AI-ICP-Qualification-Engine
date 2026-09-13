import dataclasses

from app.acquisition.service import create_acquisition_pipeline
from app.acquisition.searxng_provider import SearXNGProvider
from app.core.settings import settings


def test_create_pipeline_with_searxng(monkeypatch):
    # Le pipeline lit settings.SEARCH_PROVIDER au moment de sa création :
    # on force explicitement la valeur ici pour ne pas dépendre du .env
    # réel du poste qui exécute les tests (qui peut légitimement avoir
    # SEARCH_PROVIDER=tavily ou autre chose configuré pour un usage réel).
    monkeypatch.setattr(
        "app.acquisition.service.settings",
        dataclasses.replace(settings, SEARCH_PROVIDER="searxng"),
    )

    pipeline = create_acquisition_pipeline()

    assert isinstance(
        pipeline.search_provider,
        SearXNGProvider
    )