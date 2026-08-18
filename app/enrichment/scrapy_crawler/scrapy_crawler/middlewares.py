import ipaddress
from urllib.parse import urlparse

from scrapy.exceptions import IgnoreRequest


ROOT_HOST = "linkedin.com"


class SafeHostDownloaderMiddleware:
    """Blocks requests whose host is a raw IP literal (the direct-IP SSRF
    pattern, e.g. http://169.254.169.254/...) or that is not
    linkedin.com/*.linkedin.com, applied on every request the spider makes
    — including redirect hops, since Scrapy re-runs downloader middlewares
    for each redirected request.

    Note: unlike app.enrichment.page_fetcher.PageFetcher._assert_safe_host,
    this middleware deliberately does NOT resolve DNS to check the
    destination IP range. A blocking socket.getaddrinfo() call inside
    Scrapy's asyncio/Twisted reactor thread stalls the event loop and, in
    practice, fails outright rather than degrading gracefully. Since every
    URL reaching this spider was already validated by
    app.acquisition.url_extractor.URLExtractor (real hostname check, not a
    substring match) before being written to urls_file, and the spider only
    ever targets the single fixed linkedin.com domain, the residual risk is
    limited to LinkedIn's own infrastructure redirecting to a private IP —
    combined with Scrapy's built-in `allowed_domains` restriction on the
    spider, this is judged an acceptable trade-off. A fully DNS-validated
    version would need Twisted's non-blocking resolver, which is a
    reasonable follow-up if this ever needs hardening further.
    """

    def process_request(self, request):
        hostname = urlparse(request.url).hostname
        if not hostname:
            raise IgnoreRequest(f"URL without a valid host: {request.url}")

        hostname = hostname.lower()

        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            pass
        else:
            raise IgnoreRequest(
                f"Raw IP literal used as host, not allowed: {hostname}"
            )

        is_linkedin_host = (
            hostname == ROOT_HOST or hostname.endswith("." + ROOT_HOST)
        )
        if not is_linkedin_host:
            raise IgnoreRequest(f"Host not allowed: {hostname}")

        return None
