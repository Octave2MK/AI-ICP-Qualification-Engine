from app.ui.prospect_view import summarize_results


class FakeProspect:
    fullname = "Test Prospect"
    linkedin_url = "https://linkedin.com/in/test"


def test_summary_counts_success_errors_and_filtered():
    results = [
        {
            "prospect": FakeProspect(),
            "qualification": {
                "decision": "QUALIFIED",
                "qualification": object(),
            },
        },
        {
            "prospect": FakeProspect(),
            "qualification": {
                "status": "FILTERED",
            },
        },
        {
            "prospect": FakeProspect(),
            "qualification": {
                "status": "EXCLUDED",
            },
        },
        {
            "prospect": FakeProspect(),
            "error": "enrichment failed",
        },
    ]

    assert summarize_results(results) == {
        "successful": 1,
        "errors": 1,
        "filtered": 2,
    }


def test_summary_empty_results():
    assert summarize_results([]) == {
        "successful": 0,
        "errors": 0,
        "filtered": 0,
    }
