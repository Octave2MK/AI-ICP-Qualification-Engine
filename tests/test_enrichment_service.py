from app.enrichment.dto import ProfileData
from app.enrichment.enrichment_service import EnrichmentService


class FakeFetcher:
    def fetch(self, url: str) -> str:
        return """
        <html>
            <head>
                <title>Jean Dupont</title>
            </head>

            <body>

                Coach business

                https://example.com

                #marketing

            </body>
        </html>
        """


def test_enrichment_pipeline():
    service = EnrichmentService(
        fetcher=FakeFetcher()
    )

    profile = service.enrich(
        "https://linkedin.com/in/jean"
    )

    assert isinstance(profile, ProfileData)

    assert profile.linkedin_url.endswith("jean")

    assert "Coach business" in profile.clean_text

    assert "#" not in profile.clean_text

    assert "https://" not in profile.clean_text