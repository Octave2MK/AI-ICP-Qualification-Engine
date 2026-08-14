import json

from app.enrichment.dto import ProfileData
from app.qualification.dto import QualificationResult
from app.qualification.service import QualificationService
from app.qualification.llm.prompts import PromptBuilder
from app.qualification.parsers.json_parser import JsonParser
from app.qualification.validators.result_validator import ResultValidator


class BatchFakeLLM:
    def __init__(self):
        self.calls = 0
        self.batch_sizes = []

    def analyze(self, text):
        raise AssertionError("analyze() should not be used by qualify_batch")

    def analyze_batch(self, texts):
        self.calls += 1
        self.batch_sizes.append(len(texts))
        return [
            json.dumps(
                {
                    "profession": "Business Coach",
                    "sector": "Coaching",
                    "target_market": "B2B",
                    "offer_detected": True,
                    "icp_match": True,
                    "confidence": 0.9,
                    "evidence": ["B2B coaching"],
                    "exclusion_reason": None,
                }
            )
            for _ in texts
        ]


class TestableQualificationService(QualificationService):
    pass


def make_profile(name):
    return ProfileData(
        name=name,
        headline="Business Coach",
        about="B2B coaching",
        clean_text="Business Coach B2B",
    )


def test_qualify_batch_uses_one_llm_batch_call():
    llm = BatchFakeLLM()
    service = TestableQualificationService(
        llm=llm,
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
    )

    results = service.qualify_batch(
        [make_profile("Alice"), make_profile("Bob"), make_profile("Carol")]
    )

    assert len(results) == 3
    assert llm.calls == 1
    assert llm.batch_sizes == [3]
    assert all(isinstance(result, QualificationResult) for result in results)
