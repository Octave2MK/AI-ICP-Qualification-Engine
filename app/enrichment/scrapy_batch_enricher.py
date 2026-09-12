import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from app.enrichment.dto import ProfileData
from app.enrichment.interfaces.batch_enricher import BaseBatchEnricher
from app.exceptions.page_fetch_error import PageFetchError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRAPY_PROJECT_DIR = PROJECT_ROOT / "app" / "enrichment" / "scrapy_crawler"


class ScrapyBatchEnricher(BaseBatchEnricher):
    """Enrichit un lot d'URLs LinkedIn en une seule exécution Scrapy."""

    DEFAULT_TIMEOUT_SECONDS = 300

    def __init__(self, timeout_seconds: float | None = None):
        self._timeout_seconds = timeout_seconds or self.DEFAULT_TIMEOUT_SECONDS

    def enrich_many(self, linkedin_urls: list[str]) -> dict[str, ProfileData]:
        if not linkedin_urls:
            return {}

        # Les URLs de prospects sont stockées sans schéma par
        # URLNormalizer (ex: "linkedin.com/in/xyz"). scrapy.Request exige
        # une URL absolue et lève une ValueError sinon — sans ce
        # rétablissement, CHAQUE requête échoue dès sa construction et
        # profiles_by_url reste vide, quel que soit le contenu réel des
        # pages LinkedIn.
        normalized_urls = [self._ensure_scheme(url) for url in linkedin_urls]

        with tempfile.TemporaryDirectory(prefix="scrapy_batch_") as tmp_dir:
            urls_path = Path(tmp_dir) / "urls.json"
            output_path = Path(tmp_dir) / "output.jsonl"

            urls_path.write_text(
                json.dumps(normalized_urls), encoding="utf-8"
            )

            self._run_crawl(urls_path, output_path)
            results = self._read_results(output_path)

        # Ré-indexer sur les clés d'origine (sans schéma) pour que
        # FullICPWorkflow retrouve bien le profil via
        # prospect.linkedin_url, qui lui reste sans schéma.
        return {
            original: results[self._ensure_scheme(original)]
            for original in linkedin_urls
            if self._ensure_scheme(original) in results
        }

    @staticmethod
    def _ensure_scheme(url: str) -> str:
        if url.startswith("linkedin.com"):
            return "https://www." + url
        if not url.startswith(("http://", "https://")):
            return "https://" + url
        return url

    def _run_crawl(self, urls_path: Path, output_path: Path) -> None:
        command = [
            sys.executable,
            "-m",
            "scrapy",
            "crawl",
            "linkedin_profiles",
            "-a",
            f"urls_file={urls_path}",
            "-o",
            str(output_path),
        ]

        try:
            result = subprocess.run(
                command,
                cwd=SCRAPY_PROJECT_DIR,
                env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT)},
                timeout=self._timeout_seconds,
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise PageFetchError(
                f"Scrapy batch enrichment timed out after {self._timeout_seconds}s"
            ) from exc

        if result.returncode != 0:
            raise PageFetchError(
                "Scrapy batch enrichment failed "
                f"(exit code {result.returncode}): {result.stderr[-2000:]}"
            )

    @staticmethod
    def _read_results(output_path: Path) -> dict[str, ProfileData]:
        if not output_path.exists():
            return {}

        results: dict[str, ProfileData] = {}
        with output_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                url = data.get("linkedin_url", "")
                results[url] = ProfileData(
                    linkedin_url=url,
                    name=data.get("name", ""),
                    headline=data.get("headline", ""),
                    about=data.get("about", ""),
                    raw_text=data.get("raw_text", ""),
                    clean_text=data.get("clean_text", ""),
                    latest_post_date=data.get("latest_post_date", ""),
                    latest_post_text=data.get("latest_post_text", ""),
                )

        return results