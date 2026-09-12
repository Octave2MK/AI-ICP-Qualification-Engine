import json

import pytest

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


def make_profile(name):
    return ProfileData(
        linkedin_url=f"https://linkedin.com/in/{name.lower()}",
        name=name,
        headline="Business Coach",
        about="B2B coaching",
        raw_text="Business Coach B2B",
        clean_text="Business Coach B2B",
    )


def test_qualify_batch_uses_one_llm_batch_call():
    llm = BatchFakeLLM()
    service = QualificationService(
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


def test_qualify_batch_splits_into_chunks_above_batch_size():
    llm = BatchFakeLLM()
    service = QualificationService(
        llm=llm,
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
        batch_size=2,
    )

    profiles = [make_profile(f"Prospect{i}") for i in range(5)]

    results = service.qualify_batch(profiles)

    assert len(results) == 5
    # 5 profils, lots de 2 -> 3 appels de tailles 2, 2, 1
    assert llm.calls == 3
    assert llm.batch_sizes == [2, 2, 1]
    assert all(isinstance(result, QualificationResult) for result in results)


def test_qualify_batch_does_not_split_when_under_batch_size():
    llm = BatchFakeLLM()
    service = QualificationService(
        llm=llm,
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
        batch_size=15,
    )

    profiles = [make_profile(f"Prospect{i}") for i in range(10)]

    results = service.qualify_batch(profiles)

    assert len(results) == 10
    assert llm.calls == 1
    assert llm.batch_sizes == [10]


def test_qualify_batch_failure_in_one_chunk_does_not_run_remaining_chunks():
    class FailingSecondChunkLLM:
        def __init__(self):
            self.calls = 0

        def analyze(self, text):
            raise AssertionError("analyze() should not be used by qualify_batch")

        def analyze_batch(self, texts):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("Gemini quota exceeded")
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

    llm = FailingSecondChunkLLM()
    service = QualificationService(
        llm=llm,
        prompt_builder=PromptBuilder(),
        parser=JsonParser(),
        validator=ResultValidator(),
        batch_size=2,
    )

    profiles = [make_profile(f"Prospect{i}") for i in range(6)]

    with pytest.raises(RuntimeError, match="Gemini quota exceeded"):
        service.qualify_batch(profiles)

    # Le 3e lot (2 derniers profils) ne doit jamais être appelé une fois
    # que le 2e a échoué.
    assert llm.calls == 2