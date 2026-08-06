from app.qualification.dto import QualificationResult
from app.qualification.exceptions import InvalidQualificationError


class ResultValidator:
    def validate(self, result: QualificationResult) -> None:
        if not result.profession.strip():
            raise InvalidQualificationError("Profession is required.")

        if not result.sector.strip():
            raise InvalidQualificationError("Sector is required.")

        if not 0.0 <= result.confidence <= 1.0:
            raise InvalidQualificationError(
                "Confidence must be between 0 and 1."
            )

        if result.icp_match and not result.evidence:
            raise InvalidQualificationError(
                "Evidence is required when ICP match is True."
            )