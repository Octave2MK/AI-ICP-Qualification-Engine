from urllib.parse import urlparse
from app.acquisition.acquisition_models import ProspectCandidate


class URLNormalizer:
    """
    Normalise les URLs LinkedIn.
    """
    def normalize(
        self,
        prospect_url: ProspectCandidate
    ) -> ProspectCandidate:

        raw_url = prospect_url.url

        # Ajouter un schéma temporaire pour urlparse
        if not raw_url.startswith(
            ("http://", "https://")
        ):
            raw_url = "https://" + raw_url

        parsed = urlparse(raw_url)

        path = parsed.path.lower()

        # Supprimer slash final
        path = path.rstrip("/")

        normalized_url = (
            f"linkedin.com{path}"
        )
        return ProspectCandidate(
            url=normalized_url,
            title=prospect_url.title,
            snippet=prospect_url.snippet,
        )