from app.reporting.excel_exporter import ExcelExporter

from app.acquisition.acquisition_models import ProspectCandidate



def test_excel_export():

    exporter = ExcelExporter()


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
        "test_prospects.xlsx",
    )


    assert file.exists()

    assert file.suffix == ".xlsx"