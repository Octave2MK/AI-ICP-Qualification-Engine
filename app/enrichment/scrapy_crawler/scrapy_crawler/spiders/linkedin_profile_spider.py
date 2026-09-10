import json

import scrapy
from bs4 import BeautifulSoup

from app.enrichment.latest_post_extractor import extract_latest_post
from scrapy_crawler.items import LinkedInProfileItem


class LinkedInProfileSpider(scrapy.Spider):
    """Crawls LinkedIn profile URLs and extracts profile/post data."""

    name = "linkedin_profiles"
    allowed_domains = ["linkedin.com"]

    def __init__(self, urls_file: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not urls_file:
            raise ValueError("linkedin_profiles spider requires urls_file=<path>")
        self._urls_file = urls_file

    async def start(self):
        with open(self._urls_file, encoding="utf-8") as handle:
            urls = json.load(handle)

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.handle_error,
                meta={"linkedin_url": url},
                dont_filter=True,
            )

    def parse(self, response):
        title = response.css("title::text").get()
        headline = title.strip() if title else ""

        text_nodes = response.xpath("//text()").getall()
        raw_text = " ".join(
            node.strip() for node in text_nodes if node.strip()
        )

        soup = BeautifulSoup(response.text, "html.parser")
        latest_post_date, latest_post_text = extract_latest_post(soup)

        yield LinkedInProfileItem(
            linkedin_url=response.meta["linkedin_url"],
            name="",
            headline=headline,
            about="",
            raw_text=raw_text,
            latest_post_date=latest_post_date,
            latest_post_text=latest_post_text,
        )

    def handle_error(self, failure):
        url = failure.request.meta.get("linkedin_url", failure.request.url)
        self.logger.warning("Failed to fetch %s: %s", url, failure.value)
