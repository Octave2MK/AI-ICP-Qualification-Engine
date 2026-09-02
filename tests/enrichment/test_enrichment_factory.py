import pytest

from app.core.settings import settings
from app.enrichment.enrichment_factory import EnrichmentFactory
from app.enrichment.osint_enricher import OSINTEnricher
from app.enrichment.scrapy_batch_enricher import ScrapyBatchEnricher


def test_create_uses_configured_enrichment_engine():
    enricher = EnrichmentFactory.create()

    if settings.ENRICHMENT_ENGINE == "bs4":
        assert isinstance(enricher, OSINTEnricher)
    elif settings.ENRICHMENT_ENGINE == "scrapy":
        assert isinstance(enricher, ScrapyBatchEnricher)
    else:
        pytest.fail(
            f"Unsupported configured enrichment engine: {settings.ENRICHMENT_ENGINE}"
        )


def test_create_bs4_engine_explicitly():
    enricher = EnrichmentFactory.create("bs4")

    assert isinstance(enricher, OSINTEnricher)


def test_create_scrapy_engine():
    enricher = EnrichmentFactory.create("scrapy")

    assert isinstance(enricher, ScrapyBatchEnricher)


def test_create_normalizes_engine_name_case_and_whitespace():
    enricher = EnrichmentFactory.create("  SCRAPY  ")

    assert isinstance(enricher, ScrapyBatchEnricher)


def test_create_rejects_unknown_engine():
    with pytest.raises(ValueError, match="Unsupported enrichment engine"):
        EnrichmentFactory.create("unknown")
