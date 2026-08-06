from app.acquisition.provider_factory import ProviderFactory
from app.acquisition.duckduckgo_provider import DuckDuckGoProvider


def test_factory_returns_duckduckgo_provider():

    provider = ProviderFactory.create(
        "duckduckgo"
    )

    assert isinstance(
        provider,
        DuckDuckGoProvider
    )