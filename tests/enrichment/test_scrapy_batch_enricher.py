import json
import subprocess
from pathlib import Path

import pytest

from app.enrichment.scrapy_batch_enricher import ScrapyBatchEnricher
from app.exceptions.page_fetch_error import PageFetchError


def test_enrich_many_with_no_urls_returns_empty_dict_without_running_subprocess(
    monkeypatch,
):
    calls = []
    monkeypatch.setattr(
        subprocess, "run", lambda *a, **k: calls.append((a, k))
    )

    enricher = ScrapyBatchEnricher()
    result = enricher.enrich_many([])

    assert result == {}
    assert calls == []


def test_enrich_many_raises_page_fetch_error_on_timeout(monkeypatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="scrapy", timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)

    enricher = ScrapyBatchEnricher(timeout_seconds=1)

    with pytest.raises(PageFetchError, match="timed out"):
        enricher.enrich_many(["https://www.linkedin.com/in/someone"])


def test_enrich_many_raises_page_fetch_error_on_nonzero_exit(monkeypatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="boom"
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    enricher = ScrapyBatchEnricher()

    with pytest.raises(PageFetchError, match="exit code 1"):
        enricher.enrich_many(["https://www.linkedin.com/in/someone"])


def test_enrich_many_restores_scheme_before_writing_urls_file(monkeypatch, tmp_path):
    """URLNormalizer produit des URLs sans schéma (ex: "linkedin.com/in/x").
    scrapy.Request exige une URL absolue ; sans restauration du schéma,
    CHAQUE requête échouerait dès sa construction (ValueError: Missing
    scheme). Ce test verrouille le comportement attendu."""
    written_urls = {}

    def fake_run(command, cwd, env, timeout, capture_output, text):
        urls_file = command[command.index("-a") + 1].split("=", 1)[1]
        written_urls["value"] = json.loads(Path(urls_file).read_text())

        output_path = Path(command[command.index("-o") + 1])
        output_path.write_text(
            json.dumps(
                {
                    "linkedin_url": "https://www.linkedin.com/in/someone",
                    "name": "",
                    "headline": "Someone | LinkedIn",
                    "about": "",
                    "raw_text": "raw",
                    "latest_post_date": "",
                    "latest_post_text": "",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    enricher = ScrapyBatchEnricher()
    results = enricher.enrich_many(["linkedin.com/in/someone"])

    # L'URL écrite dans urls_file (destinée à scrapy.Request) doit avoir
    # un schéma absolu.
    assert written_urls["value"] == ["https://www.linkedin.com/in/someone"]

    # Le résultat doit être ré-indexé sur la clé d'origine (sans schéma),
    # puisque c'est celle-là que FullICPWorkflow utilise pour retrouver
    # le profil via prospect.linkedin_url.
    assert "linkedin.com/in/someone" in results
    assert results["linkedin.com/in/someone"].raw_text == "raw"