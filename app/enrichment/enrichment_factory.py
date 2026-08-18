from app.core.settings import settings
from app.enrichment.enrichment_service import EnrichmentService
from app.enrichment.osint_enricher import OSINTEnricher
from app.enrichment.page_fetcher import PageFetcher
from app.enrichment.profile_extractor import ProfileExtractor
from app.enrichment.scrapy_batch_enricher import ScrapyBatchEnricher
from app.enrichment.text_cleaner import TextCleaner


class EnrichmentFactory:
    """Sélectionne le moteur d'enrichissement OSINT selon
    settings.ENRICHMENT_ENGINE. Même pattern que LLMFactory/ProviderFactory."""

    @staticmethod
    def create(engine: str | None = None):
        engine = (engine or settings.ENRICHMENT_ENGINE).strip().lower()

        if engine == "bs4":
            return OSINTEnricher(
                EnrichmentService(
                    fetcher=PageFetcher(),
                    extractor=ProfileExtractor(),
                    cleaner=TextCleaner(),
                )
            )

        if engine == "scrapy":
            return ScrapyBatchEnricher()

        raise ValueError(f"Unsupported enrichment engine: {engine}")
