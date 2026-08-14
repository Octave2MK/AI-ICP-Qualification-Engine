from app.enrichment.dto import ProfileData
from app.qualification.dto import QualificationResult
from app.qualification.interfaces import BaseLLM
from app.qualification.llm.prompts import PromptBuilder
from app.qualification.parsers.json_parser import JsonParser
from app.qualification.validators.result_validator import ResultValidator
from app.qualification.normalization.qualification_normalizer import (
    QualificationNormalizer,
)
from app.qualification.icp.icp_definition import ICPDefinition


class QualificationService:
    def __init__(
        self,
        llm: BaseLLM,
        prompt_builder: PromptBuilder,
        parser: JsonParser,
        validator: ResultValidator,
    ) -> None:
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._parser = parser
        self._validator = validator

    def qualify(
        self,
        profile: ProfileData,
        icp: ICPDefinition | None = None,
    ) -> QualificationResult:
        prompt = self._prompt_builder.build(profile, icp)
        response = self._llm.analyze(prompt)
        return self._validate_result(self._parser.parse(response))

    def qualify_batch(
        self,
        profiles: list[ProfileData],
        icp: ICPDefinition | None = None,
    ) -> list[QualificationResult]:
        if not profiles:
            return []

        prompts = [
            self._prompt_builder.build(profile, icp)
            for profile in profiles
        ]
        responses = self._llm.analyze_batch(prompts)

        if len(responses) != len(profiles):
            raise ValueError(
                "LLM batch response count does not match profile count."
            )

        return [
            self._validate_result(self._parser.parse(response))
            for response in responses
        ]

    def _validate_result(
        self,
        result: QualificationResult,
    ) -> QualificationResult:
        result = QualificationNormalizer.normalize(result)
        self._validator.validate(result)
        return result
