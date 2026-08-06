from app.enrichment.dto import ProfileData
from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.prompts import PromptBuilder
from app.qualification.parsers.json_parser import JsonParser
from app.qualification.service import QualificationService
from app.qualification.validators.result_validator import ResultValidator


def test_qualification_pipeline():
    service = QualificationService(
        llm=FakeLLM(),
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )

    profile = ProfileData(
        linkedin_url="https://linkedin.com/in/john",
        name="John Doe",
        headline="Business Coach",
        about="Helping SMEs grow",
        raw_text="...",
        clean_text="Business Coach helping SMEs grow."
    )

    result = service.qualify(profile)

    assert result.profession == "Business Coach"
    assert result.icp_match is True
    assert result.confidence == 0.95

import json

from app.qualification.interfaces import BaseLLM


class InvalidLLM(BaseLLM):
    def analyze(self, text: str) -> str:
        return json.dumps({
            "profession": "",
            "sector": "",
            "target_market": "B2B",
            "offer_detected": True,
            "authority_signals": [],
            "content_signals": [],
            "commercial_signals": [],
            "icp_match": True,
            "confidence": 2.0,
            "evidence": [],
            "exclusion_reason": None,
        })

import pytest

from app.qualification.exceptions import InvalidQualificationError


def test_invalid_result_is_rejected():
    service = QualificationService(
        llm=InvalidLLM(),
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )

    profile = ProfileData(
        linkedin_url="",
        name="",
        headline="",
        about="",
        raw_text="",
        clean_text=""
    )

    with pytest.raises(InvalidQualificationError):
        service.qualify(profile)