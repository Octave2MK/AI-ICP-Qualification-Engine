from app.acquisition.pipeline import AcquisitionPipeline
from app.acquisition.acquisition_models import (
    ICP,
    SearchQuery,
)

from app.acquisition.query_generator import QueryGenerator
from app.acquisition.url_extractor import URLExtractor
from app.acquisition.normalizer import URLNormalizer
from app.acquisition.deduplicator import Deduplicator
from app.acquisition.prospect_mapper import ProspectMapper

from app.acquisition.search_provider import SearchProvider


class FailingProvider(SearchProvider):

    def search(
        self,
        query: SearchQuery
    ):

        raise Exception(
            "Search failed"
        )


def test_pipeline_continues_after_search_error():

    pipeline = AcquisitionPipeline(

        query_generator=QueryGenerator(),

        search_provider=FailingProvider(),

        url_extractor=URLExtractor(),

        normalizer=URLNormalizer(),

        deduplicator=Deduplicator(),

        prospect_mapper=ProspectMapper(),
    )


    result = pipeline.run(
        ICP(
            job_titles=[
                "Business Coach"
            ],
            countries=[
                "France"
            ],
        )
    )


    assert result == []