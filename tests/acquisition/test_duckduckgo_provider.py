import pytest

from app.acquisition.acquisition_models import SearchQuery
from app.acquisition.duckduckgo_provider import DuckDuckGoProvider
from app.acquisition.exceptions import SearchProviderError


@pytest.mark.integration
def test_duckduckgo_provider():
    """Hits the real DuckDuckGo/Brave backend; now that DuckDuckGoProvider
    raises on failure instead of silently returning [] (see
    SearchProviderError wiring), this test legitimately depends on external
    network reliability and belongs with the other integration tests."""

    provider = DuckDuckGoProvider()

    query = SearchQuery(
        text='site:linkedin.com/in "Business Coach" France'
    )

    results = provider.search(query)

    assert isinstance(results, list)


class _FakeRateLimiter:
    def __init__(self):
        self.wait_calls = 0

    def wait(self):
        self.wait_calls += 1


def test_search_calls_rate_limiter_before_querying(monkeypatch):
    fake_limiter = _FakeRateLimiter()
    provider = DuckDuckGoProvider(rate_limiter=fake_limiter)

    class FakeDDGS:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def text(self, *args, **kwargs):
            return []

    monkeypatch.setattr(
        "app.acquisition.duckduckgo_provider.DDGS", FakeDDGS
    )

    provider.search(SearchQuery(text="anything"))

    assert fake_limiter.wait_calls == 1


def test_search_raises_search_provider_error_on_failure(monkeypatch):
    provider = DuckDuckGoProvider(rate_limiter=_FakeRateLimiter())

    class FailingDDGS:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def text(self, *args, **kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "app.acquisition.duckduckgo_provider.DDGS", FailingDDGS
    )

    with pytest.raises(SearchProviderError):
        provider.search(SearchQuery(text="anything"))