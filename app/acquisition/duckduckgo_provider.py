from ddgs import DDGS

from app.acquisition.acquisition_models import (
    SearchQuery,
    SearchResult,
)

from app.acquisition.search_provider import SearchProvider
from app.core.logging import get_logger


logger = get_logger(__name__)


class DuckDuckGoProvider(SearchProvider):
    def search(
        self,
        query: SearchQuery,
    ) -> list[SearchResult]:

        results = []

        try:
            with DDGS() as ddgs:
                raw_results = list(
                    ddgs.text(
                        query.text,
                        max_results=10,
                    )
                )

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

        except Exception:
            logger.exception(
                "DuckDuckGo search failed for query: %s",
                query.text,
            )

        logger.debug(
            "DuckDuckGo produced %d SearchResult objects for query: %s",
            len(results),
            query.text,
        )

        return results