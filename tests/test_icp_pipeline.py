from app.database.models import Prospect

from app.enrichment.dto import ProfileData

from app.pipeline.icp_pipeline import ICPQualificationPipeline

from app.repositories.qualification_repository import QualificationRepository

from app.qualification.service import QualificationService

from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.prompts import PromptBuilder

from app.qualification.parsers.json_parser import JsonParser

from app.qualification.validators.result_validator import ResultValidator

from app.qualification.icp.icp_definition import ICPDefinition

from app.qualification.config.icp_loader import ICPLoader


def create_pipeline():

    service = QualificationService(
        llm=FakeLLM(),
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )

    loader = ICPLoader()

    return ICPQualificationPipeline(
        qualification_service=service,
        qualification_repository=QualificationRepository(),
        icp_loader=loader,
        icp_name="business_coach",
    )


def test_full_icp_pipeline_success(db_session):

    pipeline = create_pipeline()

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/jean",
        country="France",
        job_title="Business Coach",
        followers=5000,
    )

    db_session.add(prospect)
    db_session.commit()
    db_session.refresh(prospect)

    profile = ProfileData(
        linkedin_url="https://linkedin.com/in/jean",
        name="Jean Dupont",
        headline="Business Coach indépendant",
        about=(
            "J'accompagne les PME "
            "avec du coaching commercial."
        ),
        raw_text=(
            "Business coach B2B "
            "créateur de contenu LinkedIn"
        ),
        clean_text="Business coach PME",
    )

    result = pipeline.run(
        db_session,
        prospect,
        profile,
    )

    assert result["decision"].status == "QUALIFIED"

    assert result["decision"].priority == "HIGH"

    assert result["score"] > 100

    assert result["qualification"].profession != ""


def test_pipeline_excludes_student(db_session):

    pipeline = create_pipeline()

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/student",
        country="France",
        job_title="Student",
        followers=100,
    )

    db_session.add(prospect)
    db_session.commit()
    db_session.refresh(prospect)

    profile = ProfileData(
        linkedin_url="",
        name="Jean",
        headline="Étudiant marketing",
        about="Recherche un stage",
        raw_text="Student internship",
        clean_text="",
    )

    result = pipeline.run(
        db_session,
        prospect,
        profile,
    )

    assert result["status"] == "EXCLUDED"

    assert result["reason"] == "Profil étudiant"

    assert result["score"] == 0