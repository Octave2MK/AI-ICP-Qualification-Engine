from app.reporting.csv_exporter import (
    CSVExporter,
)

from app.acquisition.acquisition_models import (
    ProspectCandidate,
)



def test_csv_export():

    exporter = CSVExporter()


    prospects = [
        ProspectCandidate(
            url="linkedin.com/in/john-doe"
        ),

        ProspectCandidate(
            url="linkedin.com/in/jane-smith"
        ),
    ]


    file = exporter.export(
        prospects,
        "test_prospects.csv",
    )


    assert file.exists()


    content = file.read_text(
        encoding="utf-8"
    )


    assert (
        "linkedin.com/in/john-doe"
        in content
    )