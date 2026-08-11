from app.acquisition.service import create_acquisition_pipeline
from app.acquisition.searxng_provider import SearXNGProvider


def test_create_pipeline_with_searxng():
    pipeline = create_acquisition_pipeline()

    assert isinstance(
        pipeline.search_provider,
        SearXNGProvider
    )