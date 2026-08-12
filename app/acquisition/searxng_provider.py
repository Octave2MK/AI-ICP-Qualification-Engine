import httpx

from app.acquisition.acquisition_models import (
    SearchQuery,
    SearchResult,
)
from app.acquisition.search_provider import SearchProvider
from app.acquisition.exceptions import SearXNGError
from app.acquisition.network.retry import retry
from app.acquisition.network.rate_limiter import RateLimiter
from app.core.settings import settings
from app.core.logging import get_logger
from app.acquisition.cache.search_cache import SearchCache


class SearXNGProvider(SearchProvider):
    logger = get_logger("SearXNGProvider")

    def __init__(self):
        self.rate_limiter = RateLimiter(
            min_interval=settings.SEARCH_RATE_LIMIT_INTERVAL
        )
        self.cache = SearchCache()

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:
        # Some callers / serialized queries can contain an escaped colon
        # ("site\\:"). SearXNG expects the search operator as "site:".
        normalized_query = self._normalize_query(query.text)
        cache_key = normalized_query.lower().strip()

        cached_results = self.cache.get(cache_key)

        if cached_results is not None:
            self.logger.info(
                "Cache hit for query: %s",
                normalized_query,
            )
            return cached_results

        try:
            self.logger.info(
                "Searching SearXNG: %s",
                normalized_query,
            )

            payload = self._request(
                SearchQuery(text=normalized_query)
            )
        except httpx.TimeoutException as exc:
            self.logger.error(
                "SearXNG timeout for query: %s",
                normalized_query,
            )
            raise SearXNGError("SearXNG timeout") from exc

        except httpx.HTTPError as exc:
            self.logger.error(
                "SearXNG HTTP error for query: %s",
                normalized_query,
            )
            raise SearXNGError("SearXNG HTTP error") from exc

        results = [
            SearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                snippet=result.get("content", ""),
            )
            for result in payload.get("results", [])
            if result.get("url")
        ]

        self.logger.info(
            "SearXNG returned %s results",
            len(results),
        )

        self.cache.set(cache_key, results)
        return results

    @staticmethod
    def _normalize_query(query: str) -> str:
        """Normalize escaped SearXNG operators before sending the query."""
        return query.replace(r"site\:", "site:").strip()

    @retry(
        attempts=settings.SEARCH_RETRY_ATTEMPTS,
        delay=settings.SEARCH_RETRY_DELAY,
        exceptions=(httpx.HTTPError,),
    )
    def _request(
        self,
        query: SearchQuery,
    ) -> dict:
        self.rate_limiter.wait()

        response = httpx.get(
            f"{settings.SEARXNG_BASE_URL}/search",
            params={
                "q": query.text,
                "format": "json",
            },
            timeout=settings.SEARXNG_TIMEOUT,
        )
        response.raise_for_status()

        return response.json()
