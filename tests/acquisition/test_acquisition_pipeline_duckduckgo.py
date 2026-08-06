from app.acquisition.pipeline import AcquisitionPipeline
from app.acquisition.query_generator import QueryGenerator
from app.acquisition.duckduckgo_provider import DuckDuckGoProvider
from app.acquisition.url_extractor import URLExtractor
from app.acquisition.normalizer import URLNormalizer
from app.acquisition.deduplicator import Deduplicator
from app.acquisition.prospect_mapper import ProspectMapper

from app.acquisition.acquisition_models import ICP


def test_pipeline_duckduckgo():

    pipeline = AcquisitionPipeline(
        query_generator=QueryGenerator(),
        search_provider=DuckDuckGoProvider(),
        url_extractor=URLExtractor(),
        normalizer=URLNormalizer(),
        deduplicator=Deduplicator(),
        prospect_mapper=ProspectMapper(),
    )


    icp = ICP(
        job_titles=[
            "Business Coach"
        ],
        countries=[
            "France"
        ],
        languages=[
            "French"
        ],
        keywords=[
            "coach",
            "consultant",
            "formation"
        ]
    )


    prospects = pipeline.run_and_map(icp)

    print("\nPROSPECTS COUNT:", len(prospects))


    print("\nRESULTATS:")
    for prospect in prospects:
        print(
            "URL:",
            prospect.linkedin_url
        )
        print(
            "NAME:",
            prospect.name
        )
        print(
            "TITLE:",
            prospect.headline
        )
        print("---")

    assert isinstance(prospects, list)