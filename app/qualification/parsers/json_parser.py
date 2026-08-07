import json
import re
from app.qualification.dto import QualificationResult
from app.qualification.exceptions import InvalidQualificationError


class JsonParser:
    def parse(self, response: str) -> QualificationResult:
        try:
            cleaned = self._extract_json(response)
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise InvalidQualificationError(
                "Invalid JSON returned by LLM."
            ) from exc
        return QualificationResult(**data)


    @staticmethod
    def _extract_json(response: str) -> str:
        response = response.strip()

        if response.startswith("```"):
            response = re.sub(
                r"```json",
                "",
                response,
                flags=re.IGNORECASE,
            )
            response = response.replace(
                "```",
                "",
            )
        return response.strip()