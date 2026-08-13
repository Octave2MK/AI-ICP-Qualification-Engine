from app.acquisition.acquisition_models import (
    ICP,
    ProspectCandidate,
    SearchQuery,
    SearchResult,
)
from app.acquisition.deduplicator import Deduplicator
from app.acquisition.pipeline import AcquisitionPipeline
from app.acquisition.prospect_mapper import ProspectMapper
from app.acquisition.relevance_filter import RelevanceFilter
from app.acquisition.url_extractor import URLExtractor
from app.acquisition.normalizer import URLNormalizer


class FakeQueryGenerator:
    def generate(self, icp):
        return [
            SearchQuery(
                text='site:linkedin.com/in "Business Coach" "France"'
            )
        ]


class FakeSearchProvider:
    def search(self, query: SearchQuery):
        return [
            SearchResult(
                title="Pascal BENVENISTE - Business Coach",
                url="https://fr.linkedin.com/in/benveniste-pascal",
                snippet="Business Coach. Accompagnement des dirigeants.",
            )
        ]


def build_pipeline():
    return AcquisitionPipeline(
        query_generator=FakeQueryGenerator(),
        search_provider=FakeSearchProvider(),
        url_extractor=URLExtractor(),
        relevance_filter=RelevanceFilter(),
        normalizer=URLNormalizer(),
        deduplicator=Deduplicator(),
        prospect_mapper=ProspectMapper(),
    )


def build_icp():
    return ICP(
        job_titles=["Business Coach"],
        countries=["France"],
    )


def test_acquisition_pipeline_preserves_prospect_candidate_contract():
    pipeline = build_pipeline()

    candidates = pipeline.run(build_icp())

    assert len(candidates) == 1
    assert isinstance(candidates[0], ProspectCandidate)
    assert candidates[0].url == "linkedin.com/in/benveniste-pascal"
    assert candidates[0].title == "Pascal BENVENISTE - Business Coach"


def test_acquisition_pipeline_maps_candidates_to_prospects():
    pipeline = build_pipeline()

    prospects = pipeline.run_and_map(build_icp())

    assert len(prospects) == 1
    assert prospects[0].linkedin_url == "linkedin.com/in/benveniste-pascal"
