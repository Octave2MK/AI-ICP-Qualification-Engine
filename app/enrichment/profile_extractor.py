from bs4 import BeautifulSoup

from app.enrichment.dto import ProfileData
from app.enrichment.interfaces.extractor import BaseExtractor
from app.enrichment.latest_post_extractor import extract_latest_post


class ProfileExtractor(BaseExtractor):
    """Extrait les informations utiles d'une page HTML."""

    def extract(self, html: str, linkedin_url: str) -> ProfileData:
        soup = BeautifulSoup(html, "html.parser")
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()

        raw_text = soup.get_text(separator=" ", strip=True)
        latest_post_date, latest_post_text = extract_latest_post(soup)

        return ProfileData(
            linkedin_url=linkedin_url,
            name="",
            headline=title,
            about="",
            raw_text=raw_text,
            latest_post_date=latest_post_date,
            latest_post_text=latest_post_text,
        )
