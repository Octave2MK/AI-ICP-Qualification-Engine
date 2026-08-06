from openpyxl import load_workbook

from app.reporting.excel_exporter import (
    ExcelExporter,
)

from app.reporting.export_models import (
    ProspectExportData,
)



def test_excel_enriched_export(tmp_path):

    exporter = ExcelExporter()


    prospects = [

        ProspectExportData(

            linkedin_url="linkedin.com/in/john",

            name="John Martin",

            headline="Business Coach",

            profession="Business Coach",

            sector="Coaching",

            target_market="B2B",

            offer_detected=True,

            icp_match=True,

            confidence=0.95,

        )

    ]


    file = exporter.export(
        prospects,
        tmp_path / "prospects.xlsx",
    )


    workbook = load_workbook(
        file
    )


    sheet = workbook["Prospects"]


    assert (
        sheet["B2"].value
        ==
        "John Martin"
    )


    assert (
        sheet["I2"].value
        ==
        0.95
    )