import scrapy


class LinkedInProfileItem(scrapy.Item):
    """Mirrors app.enrichment.dto.ProfileData so results can be mapped back
    to that dataclass without loss of information."""

    linkedin_url = scrapy.Field()
    name = scrapy.Field()
    headline = scrapy.Field()
    about = scrapy.Field()
    raw_text = scrapy.Field()
    clean_text = scrapy.Field()
