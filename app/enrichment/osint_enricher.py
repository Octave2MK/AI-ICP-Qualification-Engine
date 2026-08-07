from app.enrichment.enrichment_service import EnrichmentService
from app.enrichment.dto import ProfileData


class OSINTEnricher:
    """
    Enrichit un prospect trouvé par acquisition.
    """
    def __init__(
        self,
        enrichment_service: EnrichmentService,
    ):
        self.enrichment_service = enrichment_service

    def enrich(
        self,
        linkedin_url: str,
    ) -> ProfileData:
        
        return self.enrichment_service.enrich(
            linkedin_url
        )