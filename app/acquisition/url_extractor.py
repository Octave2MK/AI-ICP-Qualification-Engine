from app.acquisition.acquisition_models import (
    SearchResult,
    ProspectCandidate,
)

class URLExtractor:
    """
    Extrait les URLs LinkedIn depuis les résultats de recherche.
    """

    LINKEDIN_PATTERN = "linkedin.com/in/"

    def extract(
        self,
        results: list[SearchResult]
    ) -> list[ProspectCandidate]:

        urls = []

        for result in results:
            if self.LINKEDIN_PATTERN in result.url:
                urls.append(
                    ProspectCandidate(
                        url=result.url,
                        title=result.title,
                        snippet=result.snippet,
                    )
                )
        return urls