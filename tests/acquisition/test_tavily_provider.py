import dataclasses

import pytest

from app.acquisition.acquisition_models import SearchQuery
from app.acquisition.exceptions import SearchProviderError
from app.acquisition.tavily_provider import TavilyProvider
from app.core.settings import settings


def _with_api_key(monkeypatch, api_key: str):
    monkeypatch.setattr(
        "app.acquisition.tavily_provider.settings",
        dataclasses.replace(settings, TAVILY_API_KEY=api_key),
    )


class _FakeRateLimiter:
    def __init__(self):
        self.wait_calls = 0

    def wait(self):
        self.wait_calls += 1


class _FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_search_calls_rate_limiter_before_querying(monkeypatch):
    _with_api_key(monkeypatch, "tvly-fake-key")

    fake_limiter = _FakeRateLimiter()
    provider = TavilyProvider(rate_limiter=fake_limiter)

    def fake_post(*args, **kwargs):
        return _FakeResponse({"results": []})

    monkeypatch.setattr(
        "app.acquisition.tavily_provider.requests.post", fake_post
    )

    provider.search(SearchQuery(text="anything"))

    assert fake_limiter.wait_calls == 1


def test_search_maps_tavily_results_to_search_results(monkeypatch):
    _with_api_key(monkeypatch, "tvly-fake-key")

    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _FakeResponse(
            {
                "results": [
                    {
                        "title": "John Doe",
                        "url": "https://linkedin.com/in/john-doe",
                        "content": "Business Coach basé en France.",
                    }
                ]
            }
        )

    monkeypatch.setattr(
        "app.acquisition.tavily_provider.requests.post", fake_post
    )

    provider = TavilyProvider(rate_limiter=_FakeRateLimiter())
    results = provider.search(
        SearchQuery(text='site:linkedin.com/in "Business Coach" France')
    )

    assert len(results) == 1
    assert results[0].title == "John Doe"
    assert results[0].url == "https://linkedin.com/in/john-doe"
    assert results[0].snippet == "Business Coach basé en France."

    assert captured["url"] == "https://api.tavily.com/search"
    assert captured["headers"]["Authorization"] == "Bearer tvly-fake-key"
    assert captured["json"]["query"] == (
        'site:linkedin.com/in "Business Coach" France'
    )


def test_search_raises_when_api_key_missing(monkeypatch):
    _with_api_key(monkeypatch, "")

    provider = TavilyProvider(rate_limiter=_FakeRateLimiter())

    with pytest.raises(SearchProviderError, match="not configured"):
        provider.search(SearchQuery(text="anything"))


def test_search_raises_search_provider_error_on_http_failure(monkeypatch):
    _with_api_key(monkeypatch, "tvly-fake-key")

    def fake_post(*args, **kwargs):
        return _FakeResponse({}, status_code=401)

    monkeypatch.setattr(
        "app.acquisition.tavily_provider.requests.post", fake_post
    )

    provider = TavilyProvider(rate_limiter=_FakeRateLimiter())

    with pytest.raises(SearchProviderError, match="Tavily search failed"):
        provider.search(SearchQuery(text="anything"))