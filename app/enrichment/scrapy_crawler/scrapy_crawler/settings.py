BOT_NAME = "scrapy_crawler"

SPIDER_MODULES = ["scrapy_crawler.spiders"]
NEWSPIDER_MODULE = "scrapy_crawler.spiders"

# LinkedIn's robots.txt disallows most crawling; the legacy `requests`-based
# PageFetcher never checked robots.txt either, so this preserves identical
# behavior rather than silently reducing the enrichment success rate.
ROBOTSTXT_OBEY = False

# Conservative concurrency: the legacy path fetches one profile at a time
# (a plain Python for-loop). Keep the same cadence here so switching engines
# does not increase request pressure on LinkedIn as a side effect.
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Mirrors app.enrichment.page_fetcher.PageFetcher.DEFAULT_TIMEOUT /
# MAX_RESPONSE_BYTES / DEFAULT_HEADERS.
DOWNLOAD_TIMEOUT = 10
DOWNLOAD_MAXSIZE = 2 * 1024 * 1024
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0 Safari/537.36"
)
DEFAULT_REQUEST_HEADERS = {
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    ),
}

DOWNLOADER_MIDDLEWARES = {
    "scrapy_crawler.middlewares.SafeHostDownloaderMiddleware": 100,
}

ITEM_PIPELINES = {
    "scrapy_crawler.pipelines.CleanTextPipeline": 300,
}

RETRY_ENABLED = True
RETRY_TIMES = 2

LOG_LEVEL = "WARNING"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
