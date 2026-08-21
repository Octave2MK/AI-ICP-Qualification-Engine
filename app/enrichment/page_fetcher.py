import ipaddress
import socket
import time
from urllib.parse import urljoin, urlparse

import requests

from app.core.settings import Settings, settings
from app.exceptions.page_fetch_error import PageFetchError
from app.enrichment.interfaces.fetcher import BaseFetcher


class PageFetcher(BaseFetcher):
    """Récupère le HTML d'une page distante avec une politique HTTP prudente."""

    MAX_RESPONSE_BYTES = 2 * 1024 * 1024
    MAX_REDIRECTS = 5
    DEFAULT_HEADERS = {
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    def __init__(self, settings: Settings = settings):
        self.settings = settings
        self.timeout = settings.PAGE_FETCHER_TIMEOUT
        self.retry_attempts = max(0, settings.PAGE_FETCHER_RETRY_ATTEMPTS)
        self.backoff_seconds = max(0.0, settings.PAGE_FETCHER_BACKOFF_SECONDS)
        self.delay_seconds = max(0.0, settings.PAGE_FETCHER_DELAY_SECONDS)
        self.headers = {
            **self.DEFAULT_HEADERS,
            "User-Agent": settings.PAGE_FETCHER_USER_AGENT,
        }
        self._last_request_at = 0.0

    def fetch(self, url: str) -> str:
        url = self._normalize_url(url)

        for _ in range(self.MAX_REDIRECTS + 1):
            self._assert_safe_host(url)
            response = self._request_with_retry(url)

            try:
                if 300 <= response.status_code < 400 and response.headers.get("Location"):
                    url = urljoin(url, response.headers["Location"])
                    continue

                response.raise_for_status()
                return self._read_capped(response)
            except requests.RequestException as exc:
                raise PageFetchError(f"Impossible de récupérer la page : {url}") from exc
            finally:
                response.close()

        raise PageFetchError(f"Trop de redirections : {url}")

    def _request_with_retry(self, url: str) -> requests.Response:
        attempts = self.retry_attempts + 1

        for attempt in range(attempts):
            # The configured delay throttles normal requests. Retry responses
            # have their own backoff policy and must not incur a second delay.
            if attempt == 0:
                self._respect_delay()
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    allow_redirects=False,
                    stream=True,
                )
            except requests.RequestException as exc:
                if attempt >= attempts - 1:
                    raise PageFetchError(
                        f"Impossible de récupérer la page : {url}"
                    ) from exc
                self._sleep_backoff(attempt)
                continue

            if response.status_code == 429:
                if attempt >= attempts - 1:
                    return response
                retry_after = self._retry_after(response)
                response.close()
                time.sleep(
                    retry_after
                    if retry_after is not None
                    else self.backoff_seconds * (2**attempt)
                )
                continue

            if 500 <= response.status_code < 600 and attempt < attempts - 1:
                response.close()
                self._sleep_backoff(attempt)
                continue

            return response

        raise PageFetchError(f"Impossible de récupérer la page : {url}")

    def _respect_delay(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        remaining = self.delay_seconds - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_request_at = time.monotonic()

    def _sleep_backoff(self, attempt: int) -> None:
        if self.backoff_seconds > 0:
            time.sleep(self.backoff_seconds * (2**attempt))

    @staticmethod
    def _retry_after(response: requests.Response) -> float | None:
        value = response.headers.get("Retry-After")
        if not value:
            return None
        try:
            return max(0.0, float(value))
        except ValueError:
            return None

    @staticmethod
    def _normalize_url(url: str) -> str:
        if url.startswith("linkedin.com"):
            return "https://www." + url
        if not url.startswith(("http://", "https://")):
            return "https://" + url
        return url

    @classmethod
    def _assert_safe_host(cls, url: str) -> None:
        """Bloque les cibles SSRF évidentes et revalide chaque redirection."""
        hostname = urlparse(url).hostname
        if not hostname:
            raise PageFetchError(f"URL sans hôte valide : {url}")

        try:
            candidates = [ipaddress.ip_address(hostname)]
        except ValueError:
            try:
                resolved = socket.getaddrinfo(hostname, None)
            except socket.gaierror as exc:
                raise PageFetchError(
                    f"Résolution DNS impossible pour : {hostname}"
                ) from exc
            candidates = [ipaddress.ip_address(info[4][0]) for info in resolved]

        for candidate in candidates:
            if (
                candidate.is_private
                or candidate.is_loopback
                or candidate.is_link_local
                or candidate.is_reserved
                or candidate.is_multicast
                or candidate.is_unspecified
            ):
                raise PageFetchError(
                    f"Hôte non autorisé (plage réseau interdite) : {hostname}"
                )

    def _read_capped(self, response: requests.Response) -> str:
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=8192):
            total += len(chunk)
            if total > self.MAX_RESPONSE_BYTES:
                raise PageFetchError(
                    "Réponse trop volumineuse "
                    f"(> {self.MAX_RESPONSE_BYTES} octets) : {response.url}"
                )
            chunks.append(chunk)

        encoding = response.encoding or response.apparent_encoding or "utf-8"
        return b"".join(chunks).decode(encoding, errors="replace")
