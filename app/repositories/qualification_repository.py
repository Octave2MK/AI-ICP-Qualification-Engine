from sqlalchemy.orm import Session
from app.database.models import Qualification
from app.qualification.dto import QualificationResult


class QualificationRepository:
    """
    Gestion de la persistance des qualifications IA.
    """
    def to_dto(
        self,
        qualification: Qualification,
    ) -> QualificationResult:
        return QualificationResult(
            profession=qualification.profession or "",

            sector=qualification.sector or "",

            target_market=qualification.target_market or "",

            offer_detected=bool(
                qualification.offer_detected
            ),

            authority_signals=(
                qualification.authority_signals.split(", ")
                if qualification.authority_signals
                else []
            ),

            content_signals=(
                qualification.content_signals.split(", ")
                if qualification.content_signals
                else []
            ),

            commercial_signals=(
                qualification.commercial_signals.split(", ")
                if qualification.commercial_signals
                else []
            ),

            icp_match=bool(
                qualification.icp_match
            ),

            confidence=float(
                qualification.confidence or 0
            ),

            evidence=(
                qualification.evidence.split(", ")
                if qualification.evidence
                else []
            ),

            exclusion_reason=qualification.exclusion_reason,
        )

    def save(
        self,
        db: Session,
        prospect_id: int,
        result: QualificationResult,
        icp_fingerprint: str | None = None,
    ) -> Qualification:

        qualification = Qualification(
            prospect_id=prospect_id,

            icp_fingerprint=icp_fingerprint,

            profession=result.profession,

            sector=result.sector,

            target_market=result.target_market,

            offer_detected=1 if result.offer_detected else 0,

            icp_match=1 if result.icp_match else 0,

            confidence=result.confidence,

            exclusion_reason=result.exclusion_reason,

            evidence=", ".join(
                result.evidence
            ),

            authority_signals=", ".join(
                result.authority_signals
            ),

            content_signals=", ".join(
                result.content_signals
            ),

            commercial_signals=", ".join(
                result.commercial_signals
            ),
        )

        db.add(qualification)

        db.commit()

        db.refresh(qualification)

        return qualification

    def get_by_prospect_id(
        self,
        db: Session,
        prospect_id: int,
    ) -> QualificationResult | None:
        """Legacy lookup kept for callers that do not use ICP-aware caching."""
        qualification = (
            db.query(Qualification)
            .filter(
                Qualification.prospect_id == prospect_id
            )
            .first()
        )

        if qualification is None:
            return None
        return self.to_dto(
            qualification
        )

    def get_by_prospect_and_icp(
        self,
        db: Session,
        prospect_id: int,
        icp_fingerprint: str,
    ) -> QualificationResult | None:
        """Return only the cached qualification for this exact ICP."""
        qualification = (
            db.query(Qualification)
            .filter(
                Qualification.prospect_id == prospect_id,
                Qualification.icp_fingerprint == icp_fingerprint,
            )
            .first()
        )

        if qualification is None:
            return None

        return self.to_dto(
            qualification
        )
