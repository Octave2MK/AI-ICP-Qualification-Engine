import pytest
import requests

from app.enrichment.page_fetcher import PageFetcher
from app.exceptions.page_fetch_error import PageFetchError


class MockResponse:
    def __init__(self, text="", status_code=200):
        self.text = text
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError()


def test_fetch_success(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse("<html>Hello</html>")

    monkeypatch.setattr(requests, "get", mock_get)

    fetcher = PageFetcher()

    html = fetcher.fetch("https://example.com")

    assert html == "<html>Hello</html>"


def test_fetch_connection_error(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.ConnectionError()

    monkeypatch.setattr(requests, "get", mock_get)

    fetcher = PageFetcher()

    with pytest.raises(PageFetchError):
        fetcher.fetch("https://example.com")


def test_fetch_timeout(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.Timeout()

    monkeypatch.setattr(requests, "get", mock_get)

    fetcher = PageFetcher()

    with pytest.raises(PageFetchError):
        fetcher.fetch("https://example.com")


def test_fetch_http_error(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse(status_code=404)

    monkeypatch.setattr(requests, "get", mock_get)

    fetcher = PageFetcher()

    with pytest.raises(PageFetchError):
        fetcher.fetch("https://example.com")