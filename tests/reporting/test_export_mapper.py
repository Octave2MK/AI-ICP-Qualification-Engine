from app.reporting.export_mapper import (
    ExportMapper,
)

from app.enrichment.dto import ProfileData

from app.qualification.dto import (
    QualificationResult,
)



def test_export_mapper():


    profile = ProfileData(

        linkedin_url="linkedin.com/in/john",

        name="John Martin",

        headline="Business Coach",

        about="",

        raw_text="",

        clean_text="",
    )


    qualification = QualificationResult(

        profession="Business Coach",

        sector="Coaching",

        target_market="B2B",

        offer_detected=True,

        icp_match=True,

        confidence=0.95,

    )


    export = ExportMapper.map(

        profile,

        qualification,

        85,

        "QUALIFIED",

    )


    assert (
        export.name
        ==
        "John Martin"
    )


    assert (
        export.icp_match
        is True
    )


    assert (
        export.confidence
        ==
        0.95
    )