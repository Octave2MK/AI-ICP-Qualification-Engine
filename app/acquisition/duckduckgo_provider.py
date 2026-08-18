from ddgs import DDGS

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


class DuckDuckGoProvider(SearchProvider):
    def __init__(self, rate_limiter: RateLimiter | None = None):
        self.rate_limiter = rate_limiter or RateLimiter(
            min_interval=settings.SEARCH_RATE_LIMIT_INTERVAL
        )

    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:

        results = []

        self.rate_limiter.wait()

        try:
            with DDGS() as ddgs:
                raw_results = list(
                    ddgs.text(
                        query.text,
                        max_results=10,
                    )
                )
        except Exception as exc:
            logger.exception(
                "DuckDuckGo search failed for query: %s",
                query.text,
            )
            raise SearchProviderError(
                f"DuckDuckGo search failed for query: {query.text}"
            ) from exc

        logger.debug(
            "DuckDuckGo returned %d raw results for query: %s",
            len(raw_results),
            query.text,
        )

        for item in raw_results:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("href", ""),
                    snippet=item.get("body", ""),
                )
            )

        logger.debug(
            "DuckDuckGo produced %d SearchResult objects for query: %s",
            len(results),
            query.text,
        )

        return results