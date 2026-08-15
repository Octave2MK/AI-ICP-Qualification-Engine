
from app.ui.prospect_view import results_to_dataframe


class FakeProspect:
    fullname = "Test Prospect"
    linkedin_url = "https://linkedin.com/in/test"
    job_title = "Business Coach"



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

    assert list(dataframe.columns) == ["Nom", "LinkedIn", "Métier", "Erreur"]
    assert dataframe.iloc[0]["Métier"] == "Business Coach"
    assert dataframe.iloc[1]["Erreur"] == "Gemini quota exceeded"

