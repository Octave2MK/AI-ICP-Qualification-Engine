from app.acquisition.acquisition_models import SearchQuery
from app.acquisition.duckduckgo_provider import DuckDuckGoProvider


def test_duckduckgo_provider():

    provider = DuckDuckGoProvider()

    query = SearchQuery(
        text='site:linkedin.com/in "Business Coach" France'
    )

    results = provider.search(query)

    assert isinstance(results, list)