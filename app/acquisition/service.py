from app.acquisition.acquisition_models import ICP
from app.acquisition.pipeline import AcquisitionPipeline
from app.repositories.prospect_repository import ProspectRepository

from app.acquisition.query_generator import QueryGenerator
from app.acquisition.url_extractor import URLExtractor
from app.acquisition.normalizer import URLNormalizer
from app.acquisition.deduplicator import Deduplicator
from app.acquisition.prospect_mapper import ProspectMapper
from app.acquisition.provider_factory import ProviderFactory
from app.core.settings import settings


class AcquisitionService:
    """
    Service métier pour l'acquisition de prospects.
    """
    def __init__(
        self,
        pipeline: AcquisitionPipeline,
        repository: ProspectRepository
    ):
        self.pipeline = pipeline
        self.repository = repository


    def acquire(
        self,
        db,
        icp: ICP
    ):

        prospects = (
            self.pipeline.run_and_map(icp)
        )

        saved_prospects = []

        for prospect in prospects:
            saved = self.repository.create_if_not_exists(
                db,
                prospect,
            )
            saved_prospects.append(saved)
        return saved_prospects

def create_acquisition_pipeline():
    return AcquisitionPipeline(

        query_generator=QueryGenerator(),

        search_provider=ProviderFactory.create(
            settings.SEARCH_PROVIDER
        ),

        url_extractor=URLExtractor(),

        normalizer=URLNormalizer(),

        deduplicator=Deduplicator(),

        prospect_mapper=ProspectMapper(),
    )