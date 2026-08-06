from app.enrichment.dto import ProfileData
from app.qualification.service import QualificationService
from app.qualification.icp.icp_definition import ICPDefinition

from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.prompts import PromptBuilder
from app.qualification.parsers.json_parser import JsonParser
from app.qualification.validators.result_validator import ResultValidator



def test_service_accepts_icp():

    service = QualificationService(
        llm=FakeLLM(),
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )


    profile = ProfileData(
        linkedin_url="",
        name="Jean",
        headline="Business Coach",
        about="",
        raw_text="",
        clean_text="Business coaching B2B",
    )


    icp = ICPDefinition(
        professions=[
            "Business Coach"
        ]
    )


    result = service.qualify(
        profile,
        icp,
    )


    assert result.profession == "Business Coach"