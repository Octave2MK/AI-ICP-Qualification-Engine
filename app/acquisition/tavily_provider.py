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

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


class TavilyProvider(SearchProvider):
    """
    Fournisseur de recherche basé sur l'API Tavily
    (https://docs.tavily.com/documentation/api-reference/endpoint/search).

    Nécessite une clé API (TAVILY_API_KEY) — inscription gratuite, 1000
    crédits/mois, sans carte bancaire requise.
    """

    def __init__(self, rate_limiter: RateLimiter | None = None):
        self.rate_limiter = rate_limiter or RateLimiter(
            min_interval=settings.SEARCH_RATE_LIMIT_INTERVAL
        )

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:

        if not settings.TAVILY_API_KEY:
            raise SearchProviderError(
                "TAVILY_API_KEY is not configured."
            )

        self.rate_limiter.wait()

        try:
            response = requests.post(
                TAVILY_SEARCH_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings.TAVILY_API_KEY}",
                },
                json={
                    "query": query.text,
                    "max_results": settings.TAVILY_MAX_RESULTS,
                },
                timeout=settings.TAVILY_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            logger.exception(
                "Tavily search failed for query: %s",
                query.text,
            )
            raise SearchProviderError(
                f"Tavily search failed for query: {query.text}"
            ) from exc

        raw_results = data.get("results", [])

        logger.debug(
            "Tavily returned %d raw results for query: %s",
            len(raw_results),
            query.text,
        )

        results = [
            SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
            )
            for item in raw_results
        ]

        logger.debug(
            "Tavily produced %d SearchResult objects for query: %s",
            len(results),
            query.text,
        )

        return results