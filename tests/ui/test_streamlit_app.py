from streamlit.testing.v1 import AppTest


def test_form_renders_with_expected_defaults():
    at = AppTest.from_file("app/ui/streamlit_app.py")
    at.run(timeout=15)

    assert not at.exception
    assert at.text_input(key=None)  # widgets rendered at all
    values = [widget.value for widget in at.text_input]
    assert "Business Coach" in values
    assert "France" in values
    assert "Coaching" in values


def test_successful_workflow_run_shows_success_and_results(monkeypatch):
    def fake_run_workflow(icp, progress_callback=None):
        if progress_callback:
            progress_callback(100, "done")
        return [
            {
                "prospect": None,
                "profile": None,
                "qualification": None,
            }
        ]

    at = AppTest.from_file("app/ui/streamlit_app.py")
    at.run(timeout=15)
    monkeypatch.setattr(
        "app.ui.workflow_runner.run_workflow", fake_run_workflow
    )

    at.button[0].click().run(timeout=15)

    assert not at.exception
    assert len(at.success) == 1
    assert "1 prospects" in at.success[0].value


def test_failed_workflow_run_shows_generic_error_not_raw_exception(
    monkeypatch,
):
    def failing_run_workflow(icp, progress_callback=None):
        raise RuntimeError("super secret internal detail")

    at = AppTest.from_file("app/ui/streamlit_app.py")
    at.run(timeout=15)
    monkeypatch.setattr(
        "app.ui.workflow_runner.run_workflow", failing_run_workflow
    )

    at.button[0].click().run(timeout=15)

    assert not at.exception
    assert len(at.error) == 1
    assert "super secret internal detail" not in at.error[0].value
    assert "journaux serveur" in at.error[0].value


def test_second_click_within_cooldown_window_is_blocked(monkeypatch):
    calls = []

    def counting_run_workflow(icp, progress_callback=None):
        calls.append(icp)
        return []

    at = AppTest.from_file("app/ui/streamlit_app.py")
    at.run(timeout=15)
    monkeypatch.setattr(
        "app.ui.workflow_runner.run_workflow", counting_run_workflow
    )

    at.button[0].click().run(timeout=15)
    at.button[0].click().run(timeout=15)

    assert len(calls) == 1
    assert len(at.warning) == 1
