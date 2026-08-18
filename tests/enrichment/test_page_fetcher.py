import socket

import pytest
import requests

from app.enrichment.page_fetcher import PageFetcher
from app.exceptions.page_fetch_error import PageFetchError


class MockResponse:
    def __init__(self, text="", status_code=200, headers=None, url="https://example.com/"):
        self._text = text
        self.status_code = status_code
        self.headers = headers or {}
        self.encoding = "utf-8"
        self.apparent_encoding = "utf-8"
        self.url = url
        self.closed = False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError()

    def iter_content(self, chunk_size=8192):
        data = self._text.encode("utf-8")
        for i in range(0, len(data), chunk_size):
            yield data[i : i + chunk_size]

    def close(self):
        self.closed = True


def _fake_getaddrinfo_public(*args, **kwargs):
    return [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0)),
    ]


def _fake_getaddrinfo_private(*args, **kwargs):
    return [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 0)),
    ]


@pytest.fixture(autouse=True)
def public_dns(monkeypatch):
    """By default, hostnames resolve to a public IP so existing tests using
    example.com stay hermetic (no real DNS lookups) and are not blocked by
    the SSRF guard."""
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo_public)


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


def test_fetch_follows_redirect_to_safe_host(monkeypatch):
    calls = []

    def mock_get(url, *args, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            return MockResponse(
                status_code=302,
                headers={"Location": "https://example.com/final"},
            )
        return MockResponse("<html>Final</html>")

    monkeypatch.setattr(requests, "get", mock_get)

    fetcher = PageFetcher()

    html = fetcher.fetch("https://example.com/start")

    assert html == "<html>Final</html>"
    assert len(calls) == 2


def test_fetch_rejects_direct_private_ip():
    fetcher = PageFetcher()

    with pytest.raises(PageFetchError):
        fetcher.fetch("http://127.0.0.1/admin")


def test_fetch_rejects_cloud_metadata_ip():
    fetcher = PageFetcher()

    with pytest.raises(PageFetchError):
        fetcher.fetch("http://169.254.169.254/latest/meta-data/")


def test_fetch_rejects_hostname_resolving_to_private_ip(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo_private)

    fetcher = PageFetcher()

    with pytest.raises(PageFetchError):
        fetcher.fetch("https://internal.example.com")


def test_fetch_rejects_redirect_to_private_ip(monkeypatch):
    def mock_get(url, *args, **kwargs):
        return MockResponse(
            status_code=302,
            headers={"Location": "http://127.0.0.1/secret"},
        )

    monkeypatch.setattr(requests, "get", mock_get)

    fetcher = PageFetcher()

    with pytest.raises(PageFetchError):
        fetcher.fetch("https://example.com/start")


def test_fetch_rejects_oversized_response(monkeypatch):
    fetcher = PageFetcher()
    monkeypatch.setattr(fetcher, "MAX_RESPONSE_BYTES", 10)

    def mock_get(*args, **kwargs):
        return MockResponse("x" * 100)

    monkeypatch.setattr(requests, "get", mock_get)

    with pytest.raises(PageFetchError):
        fetcher.fetch("https://example.com")
