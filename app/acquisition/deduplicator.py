from app.acquisition.acquisition_models import ProspectCandidate


class Deduplicator:
    """
    Supprime les URLs en double.
    """
    def deduplicate(
        self,
        urls: list[ProspectCandidate]
    ) -> list[ProspectCandidate]:

        unique_urls = []

        seen = set()


        for prospect in urls:
            if prospect.url not in seen:
                seen.add(
                    prospect.url
                )
                unique_urls.append(
                    prospect
                )
        return unique_urls