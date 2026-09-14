from bs4 import BeautifulSoup

from app.enrichment.dto import ProfileData
from app.enrichment.interfaces.extractor import BaseExtractor
from app.enrichment.latest_post_extractor import extract_latest_post


class ProfileExtractor(BaseExtractor):
    """Extrait les informations utiles d'une page HTML."""

    def extract(self, html: str, linkedin_url: str) -> ProfileData:
        soup = BeautifulSoup(html, "html.parser")
        title = self._meta_content(soup, "og:title") or self._title(soup)
        name = self._extract_name(soup, title)
        about = self._extract_about(soup)
        raw_text = soup.get_text(separator=" ", strip=True)
        latest_post_date, latest_post_text = extract_latest_post(soup)

        return ProfileData(
            linkedin_url=linkedin_url,
            name=name,
            headline=title,
            about=about,
            raw_text=raw_text,
            latest_post_date=latest_post_date,
            latest_post_text=latest_post_text,
        )

    @staticmethod
    def _title(soup: BeautifulSoup) -> str:
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        return ""

    @staticmethod
    def _meta_content(soup: BeautifulSoup, property_name: str) -> str:
        tag = soup.find("meta", attrs={"property": property_name})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return ""

    @staticmethod
    def _extract_name(soup: BeautifulSoup, title: str) -> str:
        heading = soup.find("h1")
        if heading:
            name = heading.get_text(" ", strip=True)
            if name:
                return name

        if title:
            return title.split(" | ", 1)[0].strip()
        return ""

    @staticmethod
    def _extract_about(soup: BeautifulSoup) -> str:
        description = ProfileExtractor._meta_content(soup, "og:description")
        if description:
            return description

        selectors = (
            '[data-section="about"]',
            ".pv-about-section",
            "section[id*='about']",
            "div[id*='about']",
        )
        for selector in selectors:
            section = soup.select_one(selector)
            if section:
                text = section.get_text(" ", strip=True)
                if text:
                    return text
        return ""
