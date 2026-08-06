from app.enrichment.dto import ProfileData

from app.qualification.qualification_pipeline import QualificationPipeline
from app.qualification.service import QualificationService

from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.prompts import PromptBuilder

from app.qualification.parsers.json_parser import JsonParser
from app.qualification.validators.result_validator import ResultValidator

from app.repositories.qualification_repository import QualificationRepository

from app.database.models import Prospect


def test_qualification_pipeline(db_session):

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/jean",
        country="France",
        job_title="Business Coach",
    )

    db_session.add(prospect)
    db_session.commit()
    db_session.refresh(prospect)


    profile = ProfileData(
        linkedin_url=prospect.linkedin_url,
        name="Jean Dupont",
        headline="Business Coach",
        about="J'aide les PME à développer leur activité.",
        raw_text="Business coach indépendant",
        clean_text="Business coach B2B",
    )


    service = QualificationService(
        llm=FakeLLM(),
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )


    pipeline = QualificationPipeline(
        qualification_service=service,
        repository=QualificationRepository(),
    )


    qualification = pipeline.run(
        db_session,
        prospect.id,
        profile,
    )


    assert qualification.id is not None

    assert qualification.prospect_id == prospect.id

    assert qualification.profession == "Business Coach"

    assert qualification.icp_match == 1

    assert qualification.confidence == 0.95