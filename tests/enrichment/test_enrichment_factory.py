import pytest

from app.enrichment.enrichment_factory import EnrichmentFactory
from app.enrichment.osint_enricher import OSINTEnricher
from app.enrichment.scrapy_batch_enricher import ScrapyBatchEnricher


def test_create_defaults_to_bs4_engine():
    enricher = EnrichmentFactory.create()

    assert isinstance(enricher, OSINTEnricher)


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
