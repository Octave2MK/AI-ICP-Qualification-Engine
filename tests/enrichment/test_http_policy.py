import requests

from app.core.settings import Settings
from app.enrichment.page_fetcher import PageFetcher


def test_page_fetcher_uses_configured_user_agent(monkeypatch):
    monkeypatch.setenv("PAGE_FETCHER_USER_AGENT", "AI-ICP-Test/1.0")
    fetcher = PageFetcher(settings=Settings())
    assert fetcher.headers["User-Agent"] == "AI-ICP-Test/1.0"


def test_page_fetcher_retries_429_using_retry_after(monkeypatch):
    responses = iter([429, 200])
    sleeps = []

    class Response:
        def __init__(self, status_code):
            self.status_code = status_code
            self.headers = {"Retry-After": "2"} if status_code == 429 else {}
            self.url = "https://example.com"
            self.encoding = "utf-8"
            self.apparent_encoding = "utf-8"

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(response=self)

        def iter_content(self, chunk_size=8192):
            yield b"ok"

        def close(self):
            pass

    monkeypatch.setattr(
        "app.enrichment.page_fetcher.requests.get",
        lambda *args, **kwargs: Response(next(responses)),
    )
    monkeypatch.setattr("app.enrichment.page_fetcher.time.sleep", sleeps.append)
    monkeypatch.setattr(
        "app.enrichment.page_fetcher.PageFetcher._assert_safe_host",
        lambda *_args, **_kwargs: None,
    )

    fetcher = PageFetcher()
    assert fetcher.fetch("https://example.com") == "ok"
    assert 2.0 in sleeps


def test_page_fetcher_does_not_retry_403(monkeypatch):
    calls = []

    class Response:
        status_code = 403
        headers = {}
        url = "https://example.com"

        def raise_for_status(self):
            raise requests.HTTPError(response=self)

        def close(self):
            pass

    def fake_get(*args, **kwargs):
        calls.append(1)
        return Response()

    monkeypatch.setattr("app.enrichment.page_fetcher.requests.get", fake_get)
    monkeypatch.setattr(
        "app.enrichment.page_fetcher.PageFetcher._assert_safe_host",
        lambda *_args, **_kwargs: None,
    )

    fetcher = PageFetcher()
    try:
        fetcher.fetch("https://example.com")
    except Exception:
        pass

    assert len(calls) == 1
