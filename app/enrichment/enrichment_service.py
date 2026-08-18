from app.enrichment.interfaces.fetcher import BaseFetcher
from app.enrichment.page_fetcher import PageFetcher
from app.enrichment.profile_extractor import ProfileExtractor
from app.enrichment.text_cleaner import TextCleaner
from app.enrichment.dto import ProfileData
from app.enrichment.interfaces.extractor import BaseExtractor
from app.enrichment.interfaces.cleaner import BaseCleaner
from app.core.logging import get_logger

logger = get_logger(__name__)


class EnrichmentService:
    """Orchestre l'enrichissement complet d'un profil."""
    def __init__(
            self,
            fetcher: BaseFetcher | None = None,
            extractor: BaseExtractor | None = None,
            cleaner: BaseCleaner | None = None,
    ):
        self.fetcher = fetcher or PageFetcher()
        self.extractor = extractor or ProfileExtractor()
        self.cleaner = cleaner or TextCleaner()

    def enrich(self, linkedin_url: str) -> ProfileData:
        try:
            html = self.fetcher.fetch(linkedin_url)
            profile = self.extractor.extract(
                html=html,
                linkedin_url=linkedin_url,
            )
            profile.clean_text = self.cleaner.clean(
                profile.raw_text
            )
            return profile
        except Exception:
            logger.exception(
                "Enrichment failed for %s.", linkedin_url
            )
            raise