from app.acquisition.search_provider import SearchProvider
from app.acquisition.duckduckgo_provider import DuckDuckGoProvider
from app.acquisition.searxng_provider import SearXNGProvider


class ProviderFactory:
    """
    Factory responsable de créer le moteur de recherche.
    """

    @staticmethod
    def create(
        provider_name: str = "duckduckgo",
    ) -> SearchProvider:

        provider_name = provider_name.strip().lower()

        if provider_name == "duckduckgo":
            return DuckDuckGoProvider()

        if provider_name == "searxng":
            return SearXNGProvider()

        raise ValueError(
            f"Unknown search provider: {provider_name}"
        )