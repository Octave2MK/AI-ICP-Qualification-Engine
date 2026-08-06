from app.reporting.acquisition_report import AcquisitionReport

from app.database.models import Prospect

from app.acquisition.acquisition_models import ICP



def test_generate_report():


    report = AcquisitionReport()


    prospects = [

        Prospect(
            fullname="Unknown",
            linkedin_url="linkedin.com/in/test"
        )

    ]


    icp = ICP(

        job_titles=[
            "Business Coach"
        ],

        countries=[
            "France"
        ]

    )


    output = report.generate(
        prospects,
        icp
    )


    assert (
        "Business Coach"
        in output
    )


    assert (
        "linkedin.com/in/test"
        in output
    )


    assert (
        "Prospects found: 1"
        in output
    )