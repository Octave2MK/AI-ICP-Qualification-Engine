from app.acquisition.acquisition_models import SearchQuery
from app.acquisition.search_provider import MockSearchProvider


def test_mock_provider_returns_results():

    provider = MockSearchProvider()

    results = provider.search(
        SearchQuery(text="business coach")
    )

    assert len(results) == 2

    assert results[0].title == "John Doe"

    assert "linkedin.com" in results[0].url