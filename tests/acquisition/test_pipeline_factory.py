from app.acquisition.service import (
    create_acquisition_pipeline
)

from app.acquisition.searxng_provider import (
    SearXNGProvider
)

from app.acquisition.service import create_acquisition_pipeline
from app.acquisition.duckduckgo_provider import DuckDuckGoProvider



def test_create_pipeline_with_searxng():

    pipeline = create_acquisition_pipeline()

    assert isinstance(
        pipeline.search_provider,
        DuckDuckGoProvider
    )