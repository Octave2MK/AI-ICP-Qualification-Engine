from app.reporting.csv_exporter import CSVExporter

from app.reporting.export_models import (
    ProspectExportData,
)



def test_csv_enriched_export(tmp_path):

    exporter = CSVExporter()


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


            authority_signals=[
                "Founder"
            ],

            evidence=[
                "Programme coaching PME"
            ],

        )

    ]


    file = exporter.export(
        prospects,
        tmp_path / "prospects.csv",
    )


    content = file.read_text(
        encoding="utf-8"
    )


    assert "John Martin" in content

    assert "Business Coach" in content

    assert "0.95" in content