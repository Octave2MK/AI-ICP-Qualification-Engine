import requests
from app.exceptions.page_fetch_error import PageFetchError
from app.enrichment.interfaces.fetcher import BaseFetcher


class PageFetcher(BaseFetcher):
    """Récupère le HTML d'une page distante."""

    DEFAULT_TIMEOUT = 10
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0 Safari/537.36"
        ),
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept": (
            "text/html,"
            "application/xhtml+xml,"
            "application/xml;q=0.9,"
            "*/*;q=0.8"
        ),
    }

    def fetch(self, url: str) -> str:
        if url.startswith("linkedin.com"):
            url = "https://www." + url
        elif not url.startswith(
            ("http://", "https://")
        ):
            url = "https://" + url

        try:
            response = requests.get(
                url,
                headers=self.DEFAULT_HEADERS,
                timeout=self.DEFAULT_TIMEOUT,
                allow_redirects=True,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            raise PageFetchError(
                f"Impossible de récupérer la page : {url}"
            ) from exc