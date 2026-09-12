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

DEFAULT_BATCH_SIZE = 15


class QualificationService:
    def __init__(
        self,
        llm: BaseLLM,
        prompt_builder: PromptBuilder,
        parser: JsonParser,
        validator: ResultValidator,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self._llm = llm
        self._prompt_builder = prompt_builder
        self._parser = parser
        self._validator = validator
        # Un lot unique trop volumineux augmente le rayon d'explosion (tout
        # le lot échoue ensemble en cas de réponse LLM invalide) et la
        # taille du prompt envoyé. batch_size borne chaque appel réel.
        self._batch_size = max(1, batch_size)

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

        chunks = [
            profiles[start : start + self._batch_size]
            for start in range(0, len(profiles), self._batch_size)
        ]

        logger.info(
            "Qualifying %d profile(s) via %d LLM batch call(s) "
            "(chunks of up to %d).",
            len(profiles),
            len(chunks),
            self._batch_size,
        )

        results: list[QualificationResult] = []
        start_index = 0

        for chunk in chunks:
            results.extend(self._qualify_chunk(chunk, icp, start_index))
            start_index += len(chunk)

        return results

    def _qualify_chunk(
        self,
        chunk: list[ProfileData],
        icp: ICPDefinition | None,
        start_index: int,
    ) -> list[QualificationResult]:
        prompts = [
            self._prompt_builder.build(profile, icp)
            for profile in chunk
        ]
        try:
            responses = self._llm.analyze_batch(prompts)

            if len(responses) != len(chunk):
                raise ValueError(
                    "LLM batch response count does not match profile count."
                )

            return [
                self._validate_result(self._parser.parse(response))
                for response in responses
            ]
        except Exception:
            logger.exception(
                "Batch qualification failed for profiles %d-%d.",
                start_index,
                start_index + len(chunk) - 1,
            )
            raise

    def _validate_result(
        self,
        result: QualificationResult,
    ) -> QualificationResult:
        result = QualificationNormalizer.normalize(result)
        self._validator.validate(result)
        return result