from app.pipeline.full_pipeline import FullICPWorkflow

from app.enrichment.dto import ProfileData


class FakeProspect:

    def __init__(self):
        self.id = 1
        self.linkedin_url = (
            "linkedin.com/in/john-doe"
        )


class FakeAcquisitionService:

    def acquire(self, db, icp):

        return [
            FakeProspect()
        ]



class FakeOSINTEnricher:

    def enrich(self, linkedin_url):

        return ProfileData(
            linkedin_url=linkedin_url,
            name="John Doe",
            headline="Business Coach",
            about=(
                "J'aide les entrepreneurs "
                "à développer leur activité."
            ),
            raw_text=(
                "Business Coach France"
            ),
            clean_text=(
                "business coach france"
            ),
        )



class FakeQualificationPipeline:

    def run(
        self,
        db,
        prospect,
        profile,
    ):

        return {
            "decision": "QUALIFIED",
            "score": 90,
            "profile_name": profile.name,
        }



def test_full_icp_workflow():

    workflow = FullICPWorkflow(
        acquisition_service=(
            FakeAcquisitionService()
        ),
        osint_enricher=(
            FakeOSINTEnricher()
        ),
        qualification_pipeline=(
            FakeQualificationPipeline()
        ),
    )


    results = workflow.run(
        db=None,
        icp="business_coach",
    )


    assert len(results) == 1


    result = results[0]


    assert "prospect" in result

    assert "profile" in result

    assert "qualification" in result


    assert (
        result["profile"].name
        == "John Doe"
    )


    assert (
        result["qualification"]["decision"]
        == "QUALIFIED"
    )


    assert (
        result["qualification"]["score"]
        == 90
    )