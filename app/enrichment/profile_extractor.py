from bs4 import BeautifulSoup

from app.enrichment.dto import ProfileData
from app.enrichment.interfaces.extractor import BaseExtractor


class ProfileExtractor(BaseExtractor):
    """Extrait les informations utiles d'une page HTML."""

    def extract(self, html: str, linkedin_url: str) -> ProfileData:
        soup = BeautifulSoup(html, "html.parser")

        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        raw_text = soup.get_text(separator=" ", strip=True)

        return ProfileData(
            linkedin_url=linkedin_url,
            name="",
            headline=title,
            about="",
            raw_text=raw_text,
        )