from app.pipeline.full_pipeline import FullICPWorkflow
from app.enrichment.dto import ProfileData
from app.enrichment.interfaces.batch_enricher import BaseBatchEnricher
from app.acquisition.acquisition_models import ICP


class FakeProspect:
    def __init__(self):
        self.id = 1
        self.linkedin_url = "linkedin.com/in/john-doe"


class FakeAcquisitionService:
    def acquire(self, db, icp):
        assert isinstance(icp, ICP)
        return [FakeProspect()]


class FakeOSINTEnricher:
    def enrich(self, linkedin_url):
        return ProfileData(
            linkedin_url=linkedin_url,
            name="John Doe",
            headline="Business Coach",
            about="J'aide les entrepreneurs à développer leur activité.",
            raw_text="Business Coach France",
            clean_text="business coach france",
        )


class FakeQualificationPipeline:
    def run(self, db, prospect, profile, icp):
        assert icp.professions == ["Business Coach"]
        assert icp.target_markets == ["France"]
        return {
            "decision": "QUALIFIED",
            "score": 90,
            "profile_name": profile.name,
        }


def test_full_icp_workflow():
    workflow = FullICPWorkflow(
        acquisition_service=FakeAcquisitionService(),
        osint_enricher=FakeOSINTEnricher(),
        qualification_pipeline=FakeQualificationPipeline(),
    )

    icp = ICP(
        job_titles=["Business Coach"],
        countries=["France"],
    )

    results = workflow.run(
        db=None,
        icp=icp,
    )

    assert len(results) == 1
    result = results[0]

    assert "prospect" in result
    assert "profile" in result
    assert "qualification" in result
    assert result["profile"].name == "John Doe"
    assert result["qualification"]["decision"] == "QUALIFIED"
    assert result["qualification"]["score"] == 90


class FakeBatchEnricher(BaseBatchEnricher):
    """Mimics a BaseBatchEnricher (e.g. ScrapyBatchEnricher): a single
    enrich_many() call covering every prospect's URL, rather than one
    enrich() call per prospect."""

    def __init__(self, profiles_by_url):
        self._profiles_by_url = profiles_by_url
        self.enrich_many_calls = []

    def enrich_many(self, linkedin_urls):
        self.enrich_many_calls.append(list(linkedin_urls))
        return self._profiles_by_url


def test_full_icp_workflow_uses_batch_enrichment_when_available():
    batch_enricher = FakeBatchEnricher(
        {
            "linkedin.com/in/john-doe": ProfileData(
                linkedin_url="linkedin.com/in/john-doe",
                name="John Doe",
                headline="Business Coach",
                about="",
                raw_text="",
                clean_text="business coach france",
            )
        }
    )

    workflow = FullICPWorkflow(
        acquisition_service=FakeAcquisitionService(),
        osint_enricher=batch_enricher,
        qualification_pipeline=FakeQualificationPipeline(),
    )

    icp = ICP(job_titles=["Business Coach"], countries=["France"])

    results = workflow.run(db=None, icp=icp)

    assert batch_enricher.enrich_many_calls == [["linkedin.com/in/john-doe"]]
    assert len(results) == 1
    assert results[0]["qualification"]["decision"] == "QUALIFIED"


def test_full_icp_workflow_records_error_for_url_missing_from_batch_result():
    # The batch enricher returns nothing for this prospect's URL, simulating
    # an individual crawl failure that must not fail the whole batch.
    batch_enricher = FakeBatchEnricher({})

    workflow = FullICPWorkflow(
        acquisition_service=FakeAcquisitionService(),
        osint_enricher=batch_enricher,
        qualification_pipeline=FakeQualificationPipeline(),
    )

    icp = ICP(job_titles=["Business Coach"], countries=["France"])

    results = workflow.run(db=None, icp=icp)

    assert len(results) == 1
    assert "error" in results[0]
    assert "profile" not in results[0]


def test_full_icp_workflow_records_error_for_empty_batch_profile():
    # A batch-produced ProfileData that exists but carries no exploitable
    # identity/bio content (e.g. Scrapy only captured a LinkedIn login
    # wall) must be treated as an enrichment failure, not silently passed
    # through to qualification via the acquisition fallback.
    batch_enricher = FakeBatchEnricher(
        {
            "linkedin.com/in/john-doe": ProfileData(
                linkedin_url="linkedin.com/in/john-doe",
                name="",
                headline="",
                about="",
                raw_text="Identifiez-vous pour voir le profil complet...",
            )
        }
    )

    workflow = FullICPWorkflow(
        acquisition_service=FakeAcquisitionService(),
        osint_enricher=batch_enricher,
        qualification_pipeline=FakeQualificationPipeline(),
    )

    icp = ICP(job_titles=["Business Coach"], countries=["France"])

    results = workflow.run(db=None, icp=icp)

    assert len(results) == 1
    assert "error" in results[0]
    assert "profile" not in results[0]


def test_full_icp_workflow_records_error_for_empty_one_by_one_profile():
    class EmptyOSINTEnricher:
        def enrich(self, linkedin_url):
            return ProfileData(
                linkedin_url=linkedin_url,
                name="",
                headline="",
                about="",
                raw_text="Identifiez-vous pour voir le profil complet...",
            )

    workflow = FullICPWorkflow(
        acquisition_service=FakeAcquisitionService(),
        osint_enricher=EmptyOSINTEnricher(),
        qualification_pipeline=FakeQualificationPipeline(),
    )

    icp = ICP(job_titles=["Business Coach"], countries=["France"])

    results = workflow.run(db=None, icp=icp)

    assert len(results) == 1
    assert "error" in results[0]
    assert "profile" not in results[0]