import pytest

from app.ui import workflow_runner


class _FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class _FakeWorkflow:
    def __init__(self, result=None, exc=None):
        self._result = result
        self._exc = exc
        self.run_calls = []

    def run(self, db, icp, progress_callback=None):
        self.run_calls.append(
            {"db": db, "icp": icp, "progress_callback": progress_callback}
        )
        if self._exc is not None:
            raise self._exc
        return self._result


def test_run_workflow_bootstraps_db_and_returns_workflow_result(monkeypatch):
    init_db_calls = []
    monkeypatch.setattr(
        workflow_runner, "init_db", lambda: init_db_calls.append(True)
    )

    fake_session = _FakeSession()
    monkeypatch.setattr(
        workflow_runner, "SessionLocal", lambda: fake_session
    )

    fake_workflow = _FakeWorkflow(result=["result-1"])
    monkeypatch.setattr(
        workflow_runner,
        "create_full_workflow",
        lambda db: fake_workflow,
    )

    icp = object()
    results = workflow_runner.run_workflow(icp)

    assert results == ["result-1"]
    assert init_db_calls == [True]
    assert fake_workflow.run_calls == [
        {"db": fake_session, "icp": icp, "progress_callback": None}
    ]
    assert fake_session.closed is True


def test_run_workflow_closes_session_even_if_workflow_raises(monkeypatch):
    monkeypatch.setattr(workflow_runner, "init_db", lambda: None)

    fake_session = _FakeSession()
    monkeypatch.setattr(
        workflow_runner, "SessionLocal", lambda: fake_session
    )

    fake_workflow = _FakeWorkflow(exc=RuntimeError("boom"))
    monkeypatch.setattr(
        workflow_runner,
        "create_full_workflow",
        lambda db: fake_workflow,
    )

    with pytest.raises(RuntimeError, match="boom"):
        workflow_runner.run_workflow(object())

    assert fake_session.closed is True


def test_run_workflow_forwards_progress_callback(monkeypatch):
    monkeypatch.setattr(workflow_runner, "init_db", lambda: None)
    monkeypatch.setattr(
        workflow_runner, "SessionLocal", lambda: _FakeSession()
    )

    fake_workflow = _FakeWorkflow(result=[])
    monkeypatch.setattr(
        workflow_runner,
        "create_full_workflow",
        lambda db: fake_workflow,
    )

    def progress_callback(percent, text):
        pass

    workflow_runner.run_workflow(object(), progress_callback=progress_callback)

    assert fake_workflow.run_calls[0]["progress_callback"] is progress_callback
