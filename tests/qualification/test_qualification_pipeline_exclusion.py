from app.enrichment.dto import ProfileData

from app.qualification.qualification_pipeline import QualificationPipeline

from app.qualification.service import QualificationService

from app.qualification.llm.fake_llm import FakeLLM

from app.qualification.llm.prompts import PromptBuilder

from app.qualification.parsers.json_parser import JsonParser

from app.qualification.validators.result_validator import ResultValidator

from app.repositories.qualification_repository import QualificationRepository



def test_pipeline_stops_excluded_profile():


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


    profile = ProfileData(
        linkedin_url="",
        name="Jean",
        headline="Étudiant marketing",
        about="Recherche un stage",
        raw_text="Student",
        clean_text="",
    )


    result = pipeline.run(
        None,
        1,
        profile,
    )


    assert result["excluded"] is True

    assert result["reason"] == "Profil étudiant"