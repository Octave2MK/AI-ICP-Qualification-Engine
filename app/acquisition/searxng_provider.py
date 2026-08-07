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
    logger = get_logger(
        "SearXNGProvider"
    )

    def __init__(self):
        self.rate_limiter = RateLimiter(
            min_interval=settings.SEARCH_RATE_LIMIT_INTERVAL
        )
        self.cache = SearchCache()

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:

        cache_key = query.text.lower().strip()

        cached_results = self.cache.get(
            cache_key
        )


        if cached_results is not None:
            self.logger.info(
                "Cache hit for query: %s",
                query.text,
            )
            return cached_results
        try:
            self.logger.info(
                "Searching SearXNG: %s",
                query.text,
            )

            payload = self._request(query)
        except httpx.TimeoutException as exc:

            self.logger.error(
                "SearXNG timeout for query: %s",
                query.text,
            )
            raise SearXNGError(
                "SearXNG timeout"
            ) from exc


        except httpx.HTTPError as exc:
            self.logger.error(
                "SearXNG HTTP error for query: %s",
                query.text,
            )
            raise SearXNGError(
                "SearXNG HTTP error"
            ) from exc

        results = [
            SearchResult(
                title=result["title"],
                url=result["url"],
                snippet=result.get("content", ""),
            )
            for result in payload.get("results", [])
        ]

        self.logger.info(
            "SearXNG returned %s results",
            len(results),
        )

        self.cache.set(
            cache_key,
            results,
        )
        return results

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