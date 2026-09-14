import requests

from app.acquisition.acquisition_models import (
    SearchQuery,
    SearchResult,
)

from app.acquisition.search_provider import SearchProvider
from app.acquisition.exceptions import SearchProviderError
from app.acquisition.network.rate_limiter import RateLimiter
from app.core.logging import get_logger
from app.core.settings import settings


logger = get_logger(__name__)

SERPAPI_SEARCH_URL = "https://serpapi.com/search"


class SerpApiProvider(SearchProvider):
    """
    Fournisseur de recherche basé sur SerpApi
    (https://serpapi.com/search-api), moteur "google" par défaut.

    Nécessite une clé API (SERPAPI_API_KEY).
    """

    def __init__(self, rate_limiter: RateLimiter | None = None):
        self.rate_limiter = rate_limiter or RateLimiter(
            min_interval=settings.SEARCH_RATE_LIMIT_INTERVAL
        )

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:

        if not settings.SERPAPI_API_KEY:
            raise SearchProviderError(
                "SERPAPI_API_KEY is not configured."
            )

        self.rate_limiter.wait()

        try:
            response = requests.get(
                SERPAPI_SEARCH_URL,
                params={
                    "q": query.text,
                    "engine": "google",
                    "api_key": settings.SERPAPI_API_KEY,
                    "num": str(settings.SERPAPI_MAX_RESULTS),
                },
                timeout=settings.SERPAPI_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.exception(
                "SerpApi search failed for query: %s",
                query.text,
            )
            raise SearchProviderError(
                f"SerpApi search failed for query: {query.text}"
            ) from exc

        if data.get("search_metadata", {}).get("status") == "Error":
            error_message = data.get("error", "unknown error")
            logger.error(
                "SerpApi returned an error for query '%s': %s",
                query.text,
                error_message,
            )
            raise SearchProviderError(
                f"SerpApi search failed for query: {query.text} "
                f"({error_message})"
            )

        raw_results = data.get("organic_results", [])

        logger.debug(
            "SerpApi returned %d raw results for query: %s",
            len(raw_results),
            query.text,
        )

        results = [
            SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
            )
            for item in raw_results
        ]

        logger.debug(
            "SerpApi produced %d SearchResult objects for query: %s",
            len(results),
            query.text,
        )

        return results