import os

BOT_NAME = "scrapy_crawler"

SPIDER_MODULES = ["scrapy_crawler.spiders"]
NEWSPIDER_MODULE = "scrapy_crawler.spiders"

# Respect the existing crawler behavior. This is an application-level
# enrichment crawler, not an anti-bot bypass mechanism.
ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = int(os.getenv("SCRAPY_CONCURRENT_REQUESTS", "4"))
CONCURRENT_REQUESTS_PER_DOMAIN = int(
    os.getenv("SCRAPY_CONCURRENT_REQUESTS_PER_DOMAIN", "1")
)
DOWNLOAD_DELAY = float(os.getenv("PAGE_FETCHER_DELAY_SECONDS", "1"))

DOWNLOAD_TIMEOUT = int(os.getenv("PAGE_FETCHER_TIMEOUT", "10"))
DOWNLOAD_MAXSIZE = 2 * 1024 * 1024
USER_AGENT = os.getenv(
    "PAGE_FETCHER_USER_AGENT",
    "AI-ICP-Qualification-Engine/1.0",
)
DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy_crawler.middlewares.SafeHostDownloaderMiddleware": 100,
}

ITEM_PIPELINES = {
    "scrapy_crawler.pipelines.CleanTextPipeline": 300,
}

RETRY_ENABLED = True
RETRY_TIMES = int(os.getenv("PAGE_FETCHER_RETRY_ATTEMPTS", "2"))
RETRY_HTTP_CODES = [408, 425, 429, 500, 502, 503, 504]

LOG_LEVEL = "WARNING"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
