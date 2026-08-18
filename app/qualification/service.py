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
from app.core.logging import get_logger

logger = get_logger(__name__)


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
        try:
            response = self._llm.analyze(prompt)
            return self._validate_result(self._parser.parse(response))
        except Exception:
            logger.exception(
                "Qualification failed for profile %s.",
                getattr(profile, "linkedin_url", None),
            )
            raise

    def qualify_batch(
        self,
        profiles: list[ProfileData],
        icp: ICPDefinition | None = None,
    ) -> list[QualificationResult]:
        if not profiles:
            return []

        logger.info("Qualifying %d profile(s) via one LLM batch call.", len(profiles))

        prompts = [
            self._prompt_builder.build(profile, icp)
            for profile in profiles
        ]
        try:
            responses = self._llm.analyze_batch(prompts)

            if len(responses) != len(profiles):
                raise ValueError(
                    "LLM batch response count does not match profile count."
                )

            return [
                self._validate_result(self._parser.parse(response))
                for response in responses
            ]
        except Exception:
            logger.exception(
                "Batch qualification failed for %d profile(s).", len(profiles)
            )
            raise

    def _validate_result(
        self,
        result: QualificationResult,
    ) -> QualificationResult:
        result = QualificationNormalizer.normalize(result)
        self._validator.validate(result)
        return result
