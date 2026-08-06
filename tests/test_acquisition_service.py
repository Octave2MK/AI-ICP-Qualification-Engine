from app.acquisition.acquisition_models import ICP

from app.acquisition.service import AcquisitionService

from app.acquisition.pipeline import AcquisitionPipeline

from app.acquisition.query_generator import QueryGenerator

from app.acquisition.search_provider import MockSearchProvider

from app.acquisition.url_extractor import URLExtractor

from app.acquisition.normalizer import URLNormalizer

from app.acquisition.deduplicator import Deduplicator

from app.repositories.prospect_repository import ProspectRepository

from app.acquisition.prospect_mapper import ProspectMapper



def test_acquisition_service(db_session):


    pipeline = AcquisitionPipeline(

        query_generator=QueryGenerator(),

        search_provider=MockSearchProvider(),

        url_extractor=URLExtractor(),

        normalizer=URLNormalizer(),

        deduplicator=Deduplicator(),

        prospect_mapper=ProspectMapper()

    )


    repository = ProspectRepository()


    service = AcquisitionService(
        pipeline,
        repository
    )


    icp = ICP(

        job_titles=[
            "Business Coach"
        ],

        countries=[
            "France"
        ]

    )


    prospects = service.acquire(    
        db_session,
        icp,
    )



    assert len(prospects) == 2


    assert (
        prospects[0].linkedin_url ==
        "linkedin.com/in/john-doe"
    )


    assert prospects[0].id is not None