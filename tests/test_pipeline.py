from app.acquisition.acquisition_models import ICP

from app.acquisition.pipeline import AcquisitionPipeline

from app.acquisition.query_generator import QueryGenerator

from app.acquisition.search_provider import MockSearchProvider

from app.acquisition.url_extractor import URLExtractor

from app.acquisition.relevance_filter import RelevanceFilter

from app.acquisition.normalizer import URLNormalizer

from app.acquisition.deduplicator import Deduplicator

from app.acquisition.prospect_mapper import ProspectMapper


def test_full_acquisition_pipeline():


    pipeline = AcquisitionPipeline(

        query_generator=QueryGenerator(),

        search_provider=MockSearchProvider(),

        url_extractor=URLExtractor(),

        relevance_filter=RelevanceFilter(),

        normalizer=URLNormalizer(),

        deduplicator=Deduplicator(),

        prospect_mapper = ProspectMapper()

    )



    icp = ICP(

        job_titles=[
            "Business Coach"
        ],

        countries=[
            "France"
        ]

    )



    results = pipeline.run(icp)



    assert len(results) == 2


    assert (
        results[0].url ==
        "linkedin.com/in/john-doe"
    )