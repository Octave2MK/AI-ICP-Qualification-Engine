# HTTP fetch policy

The enrichment layer uses a conservative HTTP policy shared by the legacy `requests` fetcher and the Scrapy crawler.

## Configuration

The following environment variables are optional:

- `PAGE_FETCHER_USER_AGENT`: client User-Agent. Default: `AI-ICP-Qualification-Engine/1.0`.
- `PAGE_FETCHER_TIMEOUT`: request timeout in seconds. Default: `10`.
- `PAGE_FETCHER_RETRY_ATTEMPTS`: bounded retry count. Default: `2`.
- `PAGE_FETCHER_BACKOFF_SECONDS`: exponential-backoff base delay. Default: `2`.
- `PAGE_FETCHER_DELAY_SECONDS`: minimum delay between requests made by the legacy fetcher. Default: `1`.
- `SCRAPY_CONCURRENT_REQUESTS`: Scrapy global concurrency. Default: `4`.
- `SCRAPY_CONCURRENT_REQUESTS_PER_DOMAIN`: per-domain concurrency. Default: `1`.

HTTP 429 responses honor a numeric `Retry-After` header when present. HTTP 5xx responses and request exceptions use bounded exponential backoff. HTTP 403 responses are not retried.

This policy is intended to reduce accidental request pressure and make behavior predictable. It does not rotate identities, IP addresses, or User-Agents to bypass CAPTCHA or other access controls.
