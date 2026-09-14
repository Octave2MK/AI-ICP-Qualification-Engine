import pytest

from app.acquisition.provider_factory import ProviderFactory
from app.acquisition.duckduckgo_provider import DuckDuckGoProvider
from app.acquisition.searxng_provider import SearXNGProvider
from app.acquisition.tavily_provider import TavilyProvider
from app.acquisition.serpapi_provider import SerpApiProvider


def test_factory_returns_duckduckgo_provider():
    provider = ProviderFactory.create("duckduckgo")

    assert isinstance(
        provider,
        DuckDuckGoProvider
    )


def test_factory_returns_searxng_provider():
    provider = ProviderFactory.create("searxng")

    assert isinstance(
        provider,
        SearXNGProvider
    )


def test_factory_returns_tavily_provider():
    provider = ProviderFactory.create("tavily")

    assert isinstance(
        provider,
        TavilyProvider
    )


def test_factory_returns_serpapi_provider():
    provider = ProviderFactory.create("serpapi")

    assert isinstance(
        provider,
        SerpApiProvider
    )


def test_factory_normalizes_provider_name():
    provider = ProviderFactory.create("  SEARXNG  ")

    assert isinstance(
        provider,
        SearXNGProvider
    )


def test_factory_rejects_unknown_provider():
    with pytest.raises(
        ValueError,
        match="Unknown search provider"
    ):
        ProviderFactory.create("unknown")