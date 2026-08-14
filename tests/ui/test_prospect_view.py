from types import SimpleNamespace

from app.ui.prospect_view import results_to_dataframe, summarize_results


class FakeProspect:
    fullname = "Test Prospect"
    linkedin_url = "https://linkedin.com/in/test"
    job_title = "Business Coach"


def test_summary_counts_qualified_errors_and_filtered():
    results = [
        {
            "prospect": FakeProspect(),
            "decision": SimpleNamespace(status="QUALIFIED"),
            "qualification": object(),
        },
        {
            "prospect": FakeProspect(),
            "status": "FILTERED",
        },
        {
            "prospect": FakeProspect(),
            "status": "EXCLUDED",
        },
        {
            "prospect": FakeProspect(),
            "decision": SimpleNamespace(status="REJECTED"),
            "qualification": object(),
        },
        {
            "prospect": FakeProspect(),
            "decision": SimpleNamespace(status="REVIEW"),
            "qualification": object(),
        },
        {
            "prospect": FakeProspect(),
            "error": "enrichment failed",
        },
    ]

    assert summarize_results(results) == {
        "successful": 1,
        "errors": 1,
        "filtered": 4,
    }


def test_summary_does_not_count_ai_rejected_as_successful():
    results = [
        {
            "prospect": FakeProspect(),
            "decision": SimpleNamespace(status="REJECTED"),
            "qualification": object(),
        }
    ]

    assert summarize_results(results) == {
        "successful": 0,
        "errors": 0,
        "filtered": 1,
    }


def test_summary_counts_actual_workflow_qualified_shape():
    results = [
        {
            "prospect": FakeProspect(),
            "decision": SimpleNamespace(status="QUALIFIED"),
            "qualification": SimpleNamespace(
                profession="Business Coach",
                sector="Consulting",
            ),
            "score": 85,
        }
    ]

    assert summarize_results(results) == {
        "successful": 1,
        "errors": 0,
        "filtered": 0,
    }


def test_results_table_contains_only_requested_columns():
    dataframe = results_to_dataframe(
        [
            {
                "prospect": FakeProspect(),
                "qualification": {},
            },
            {
                "prospect": FakeProspect(),
                "error": "Gemini quota exceeded",
            },
        ]
    )

    assert list(dataframe.columns) == ["Nom", "LinkedIn", "Erreur", "Métier"]
    assert dataframe.iloc[0]["Métier"] == "Business Coach"
    assert dataframe.iloc[1]["Erreur"] == "Gemini quota exceeded"


def test_summary_empty_results():
    assert summarize_results([]) == {
        "successful": 0,
        "errors": 0,
        "filtered": 0,
    }
