import scrapy


class LinkedInProfileItem(scrapy.Item):
    """Mirrors app.enrichment.dto.ProfileData for result mapping."""

    linkedin_url = scrapy.Field()
    name = scrapy.Field()
    headline = scrapy.Field()
    about = scrapy.Field()
    raw_text = scrapy.Field()
    clean_text = scrapy.Field()
    latest_post_date = scrapy.Field()
    latest_post_text = scrapy.Field()
