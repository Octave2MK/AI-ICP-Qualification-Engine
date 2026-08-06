from app.acquisition.search_provider import SearchProvider
from app.acquisition.duckduckgo_provider import DuckDuckGoProvider


class ProviderFactory:
    """
    Factory responsable de créer le moteur de recherche.
    """

    @staticmethod
    def create(
        provider_name: str = "duckduckgo",
    ) -> SearchProvider:

        if provider_name == "duckduckgo":
            return DuckDuckGoProvider()

        raise ValueError(
            f"Unknown search provider: {provider_name}"
        )