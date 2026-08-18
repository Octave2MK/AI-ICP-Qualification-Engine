import pytest

from app.enrichment.scrapy_batch_enricher import ScrapyBatchEnricher

pytestmark = pytest.mark.integration


def test_enrich_many_crawls_a_real_linkedin_profile():
    enricher = ScrapyBatchEnricher(timeout_seconds=60)

    results = enricher.enrich_many(
        ["https://www.linkedin.com/in/satyanadella"]
    )

    assert "https://www.linkedin.com/in/satyanadella" in results
    profile = results["https://www.linkedin.com/in/satyanadella"]
    assert profile.headline
    assert profile.raw_text
    assert profile.clean_text
