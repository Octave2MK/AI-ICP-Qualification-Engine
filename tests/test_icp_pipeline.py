import pytest

from app.database.models import Prospect, Qualification
from app.enrichment.dto import ProfileData
from app.pipeline.icp_pipeline import ICPQualificationPipeline
from app.qualification.exceptions import InvalidQualificationError
from app.repositories.qualification_repository import QualificationRepository
from app.qualification.service import QualificationService
from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.prompts import PromptBuilder
from app.qualification.parsers.json_parser import JsonParser
from app.qualification.validators.result_validator import ResultValidator
from app.qualification.icp.icp_definition import ICPDefinition


def create_pipeline(llm=None):
    service = QualificationService(
        llm=llm or FakeLLM(),
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )

    return ICPQualificationPipeline(
        qualification_service=service,
        qualification_repository=QualificationRepository(),
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
        about="J'accompagne les PME avec du coaching commercial.",
        raw_text="Business coach B2B créateur de contenu LinkedIn",
        clean_text="Business coach PME",
    )

    icp = ICPDefinition(
        professions=["Business Coach"],
        sectors=["Coaching"],
        target_markets=["France"],
    )

    result = pipeline.run(
        db_session,
        prospect,
        profile,
        icp,
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

    icp = ICPDefinition(
        professions=["Business Coach"],
        target_markets=["France"],
        forbidden_keywords=["étudiant", "stage", "student", "internship"],
    )

    result = pipeline.run(
        db_session,
        prospect,
        profile,
        icp,
    )

    assert result["status"] == "EXCLUDED"
    assert result["reason"] == "Profil étudiant"
    assert result["score"] == 0


def test_qualification_cache_is_isolated_by_icp(db_session):
    pipeline = create_pipeline()

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/multi-icp",
        country="France",
        job_title="Business Coach",
        followers=5000,
    )

    db_session.add(prospect)
    db_session.commit()
    db_session.refresh(prospect)

    profile = ProfileData(
        linkedin_url="https://linkedin.com/in/multi-icp",
        name="Jean Dupont",
        headline="Business Coach indépendant",
        about="J'accompagne les PME avec du coaching commercial.",
        raw_text="Business coach B2B créateur de contenu LinkedIn",
        clean_text="Business coach PME",
    )

    france_icp = ICPDefinition(
        professions=["Business Coach"],
        sectors=["Coaching"],
        target_markets=["France"],
    )

    belgium_icp = ICPDefinition(
        professions=["Business Coach"],
        sectors=["Coaching"],
        target_markets=["Belgique"],
    )

    first = pipeline.run(
        db_session,
        prospect,
        profile,
        france_icp,
    )

    second = pipeline.run(
        db_session,
        prospect,
        profile,
        belgium_icp,
    )

    assert first["cached"] is False
    assert second["cached"] is False
    assert db_session.query(Qualification).count() == 2

    repeated = pipeline.run(
        db_session,
        prospect,
        profile,
        france_icp,
    )

    assert repeated["cached"] is True
    assert db_session.query(Qualification).count() == 2


def test_pipeline_marks_low_confidence_profile_for_review(db_session):
    low_confidence_llm = FakeLLM(
        response={
            "profession": "Business Coach",
            "sector": "Consulting",
            "target_market": "B2B",
            "offer_detected": True,
            "authority_signals": [],
            "content_signals": [],
            "commercial_signals": [],
            "icp_match": True,
            "confidence": 0.5,
            "evidence": ["Mentions coaching"],
            "exclusion_reason": None,
        }
    )
    pipeline = create_pipeline(llm=low_confidence_llm)

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/low-confidence",
        country="France",
        job_title="Business Coach",
        followers=100,
    )

    db_session.add(prospect)
    db_session.commit()
    db_session.refresh(prospect)

    profile = ProfileData(
        linkedin_url="https://linkedin.com/in/low-confidence",
        name="Jean Dupont",
        headline="Business Coach",
        about="",
        raw_text="",
        clean_text="Business coach",
    )

    icp = ICPDefinition(
        professions=["Business Coach"],
        target_markets=["France"],
        minimum_confidence=0.85,
    )

    result = pipeline.run(db_session, prospect, profile, icp)

    assert result["decision"].status == "REVIEW"
    assert result["decision"].priority == "MEDIUM"


def test_pipeline_propagates_error_on_malformed_llm_response(db_session):
    broken_llm = FakeLLM(response="this is not valid JSON")
    pipeline = create_pipeline(llm=broken_llm)

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/broken-response",
        country="France",
        job_title="Business Coach",
        followers=100,
    )

    db_session.add(prospect)
    db_session.commit()
    db_session.refresh(prospect)

    profile = ProfileData(
        linkedin_url="https://linkedin.com/in/broken-response",
        name="Jean Dupont",
        headline="Business Coach",
        about="",
        raw_text="",
        clean_text="Business coach",
    )

    icp = ICPDefinition(
        professions=["Business Coach"],
        target_markets=["France"],
    )

    with pytest.raises(InvalidQualificationError):
        pipeline.run(db_session, prospect, profile, icp)


def test_icp_fingerprint_is_deterministic():
    first = ICPDefinition(
        professions=["Business Coach", "Consultant"],
        sectors=["Coaching"],
        target_markets=["France", "Belgique"],
        required_keywords=["B2B", "dirigeant"],
        forbidden_keywords=["étudiant"],
        minimum_confidence=0.8,
    )

    same_data_different_order = ICPDefinition(
        professions=["Consultant", "Business Coach"],
        sectors=["Coaching"],
        target_markets=["Belgique", "France"],
        required_keywords=["dirigeant", "B2B"],
        forbidden_keywords=["étudiant"],
        minimum_confidence=0.8,
    )

    assert first.fingerprint() == same_data_different_order.fingerprint()
