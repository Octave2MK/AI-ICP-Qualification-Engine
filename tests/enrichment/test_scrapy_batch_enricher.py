import subprocess

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
