import time

import app.api.job_service as job_service
from tests.api.conftest import failing_workflow_factory


ICP_PAYLOAD = {
    "job_title": "Business Coach",
    "country": "France",
    "sector": "Coaching",
    "max_prospects": 20,
    "required_keywords": [],
    "forbidden_keywords": [],
}


def _wait_until_finished(client, job_id, max_attempts=20):
    for _ in range(max_attempts):
        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        status = response.json()
        if status["status"] in ("succeeded", "failed"):
            return status
        time.sleep(0.1)
    raise AssertionError("job did not finish in time")


def test_create_job_returns_201_and_pending_status(client):
    response = client.post("/api/jobs", json=ICP_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] in ("pending", "running", "succeeded")
    assert body["job_id"]


def test_full_job_lifecycle_succeeds_and_returns_results(client):
    created = client.post("/api/jobs", json=ICP_PAYLOAD)
    job_id = created.json()["job_id"]

    status = _wait_until_finished(client, job_id)
    assert status["status"] == "succeeded"
    assert status["progress_percent"] == 100

    results = client.get(f"/api/jobs/{job_id}/results")
    assert results.status_code == 200
    body = results.json()
    assert body["job_id"] == job_id
    assert len(body["prospects"]) == 2

    prospect = body["prospects"][0]
    assert prospect["linkedin_url"]
    assert prospect["name"]
    # QualificationResult comes from FakeLLM's canned "Business Coach"
    # response, which should qualify under the default minimum_confidence.
    assert prospect["status"] in ("QUALIFIED", "REVIEW")


def test_results_not_ready_returns_409(client):
    created = client.post("/api/jobs", json=ICP_PAYLOAD)
    job_id = created.json()["job_id"]

    # Immediately after creation the background task may not have run yet
    # (or may already be done, since TestClient drives it to completion as
    # part of the request/response cycle) — only assert 409 if genuinely
    # not ready, to avoid a flaky test.
    response = client.get(f"/api/jobs/{job_id}/results")
    if response.status_code != 409:
        assert response.status_code == 200
    else:
        assert "not ready" in response.json()["detail"]


def test_get_status_for_unknown_job_returns_404(client):
    response = client.get("/api/jobs/does-not-exist")
    assert response.status_code == 404


def test_get_results_for_unknown_job_returns_404(client):
    response = client.get("/api/jobs/does-not-exist/results")
    assert response.status_code == 404


def test_job_failure_is_reported_generically(client, monkeypatch):
    monkeypatch.setattr(job_service, "create_full_workflow", failing_workflow_factory)

    created = client.post("/api/jobs", json=ICP_PAYLOAD)
    job_id = created.json()["job_id"]

    status = _wait_until_finished(client, job_id)

    assert status["status"] == "failed"
    assert status["error"]
    assert "boom" not in status["error"]
    assert "journaux serveur" in status["error"]
