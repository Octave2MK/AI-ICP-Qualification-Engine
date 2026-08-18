from urllib.parse import urlparse

from app.acquisition.acquisition_models import (
    SearchResult,
    ProspectCandidate,
)

class URLExtractor:
    """
    Extrait les URLs de profils LinkedIn depuis les résultats de recherche.
    """

    ROOT_HOST = "linkedin.com"
    PROFILE_PATH_PREFIX = "/in/"

    def extract(
        self,
        results: list[SearchResult]
    ) -> list[ProspectCandidate]:

        urls = []

        for result in results:
            if self._is_linkedin_profile_url(result.url):
                urls.append(
                    ProspectCandidate(
                        url=result.url,
                        title=result.title,
                        snippet=result.snippet,
                    )
                )
        return urls

    @classmethod
    def _is_linkedin_profile_url(cls, url: str) -> bool:
        """Valide le véritable hôte de l'URL (linkedin.com ou l'un de ses
        sous-domaines, ex. fr.linkedin.com) plutôt qu'un test de
        sous-chaîne, pour éviter qu'une URL usurpée (ex. host attaquant
        contenant "linkedin.com/in/" dans son chemin) ne soit acceptée."""
        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        is_linkedin_host = (
            hostname == cls.ROOT_HOST
            or hostname.endswith("." + cls.ROOT_HOST)
        )
        return is_linkedin_host and cls.PROFILE_PATH_PREFIX in parsed.path
