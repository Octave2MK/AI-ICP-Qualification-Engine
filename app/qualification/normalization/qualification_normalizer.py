from app.qualification.dto import QualificationResult
from app.qualification.normalization.profession_normalizer import (
    ProfessionNormalizer,
)
from app.qualification.normalization.sector_normalizer import (
    SectorNormalizer,
)


class QualificationNormalizer:

    @staticmethod
    def normalize(
        result: QualificationResult,
    ) -> QualificationResult:

        result.profession = ProfessionNormalizer.normalize(
            result.profession
        )

        result.sector = SectorNormalizer.normalize(
            result.sector
        )

        return result