import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests
from app.exceptions.page_fetch_error import PageFetchError
from app.enrichment.interfaces.fetcher import BaseFetcher


class PageFetcher(BaseFetcher):
    """Récupère le HTML d'une page distante."""

    DEFAULT_TIMEOUT = 10
    MAX_RESPONSE_BYTES = 2 * 1024 * 1024
    MAX_REDIRECTS = 5
    DEFAULT_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0 Safari/537.36"
        ),
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept": (
            "text/html,"
            "application/xhtml+xml,"
            "application/xml;q=0.9,"
            "*/*;q=0.8"
        ),
    }

    def fetch(self, url: str) -> str:
        url = self._normalize_url(url)

        for _ in range(self.MAX_REDIRECTS + 1):
            self._assert_safe_host(url)

            try:
                response = requests.get(
                    url,
                    headers=self.DEFAULT_HEADERS,
                    timeout=self.DEFAULT_TIMEOUT,
                    allow_redirects=False,
                    stream=True,
                )
            except requests.RequestException as exc:
                raise PageFetchError(
                    f"Impossible de récupérer la page : {url}"
                ) from exc

            try:
                if 300 <= response.status_code < 400 and response.headers.get(
                    "Location"
                ):
                    url = urljoin(url, response.headers["Location"])
                    continue

                response.raise_for_status()
                return self._read_capped(response)
            except requests.RequestException as exc:
                raise PageFetchError(
                    f"Impossible de récupérer la page : {url}"
                ) from exc
            finally:
                response.close()

        raise PageFetchError(f"Trop de redirections : {url}")

    @staticmethod
    def _normalize_url(url: str) -> str:
        if url.startswith("linkedin.com"):
            return "https://www." + url
        if not url.startswith(("http://", "https://")):
            return "https://" + url
        return url

    @classmethod
    def _assert_safe_host(cls, url: str) -> None:
        """Bloque les cibles SSRF évidentes : IP privées/loopback/link-local
        (y compris les IP de métadonnées cloud) portées directement dans l'URL
        ou résolues via DNS. Revalidé à chaque saut de redirection."""
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
            candidates = [
                ipaddress.ip_address(info[4][0]) for info in resolved
            ]

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
