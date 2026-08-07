from ddgs import DDGS

from app.acquisition.acquisition_models import (
    SearchQuery,
    SearchResult,
)

from app.acquisition.search_provider import SearchProvider


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

                print(
                    "RAW DDG COUNT:",
                    len(raw_results)
                )

                for item in raw_results:
                    print(
                        "ITEM:",
                        item
                    )
                    results.append(
                        SearchResult(
                            title=item.get(
                                "title",
                                ""
                            ),
                            url=item.get(
                                "href",
                                ""
                            ),
                            snippet=item.get(
                                "body",
                                ""
                            ),
                        )
                    )
        except Exception as exc:
            print(
                "DDG ERROR:",
                exc
            )

        print(
            "SEARCHRESULT COUNT:",
            len(results)
        )
        return results