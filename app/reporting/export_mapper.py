from app.reporting.export_models import (
    ProspectExportData,
)



class ExportMapper:
    """
    Transforme les résultats du pipeline
    en données exportables.
    """


    @staticmethod
    def map(
        profile,
        qualification,
        score: float,
        decision,
    ) -> ProspectExportData:


        return ProspectExportData(

            linkedin_url=profile.linkedin_url,

            name=profile.name,

            headline=profile.headline,


            profession=qualification.profession,

            sector=qualification.sector,

            target_market=qualification.target_market,


            offer_detected=qualification.offer_detected,

            icp_match=qualification.icp_match,


            confidence=qualification.confidence,


            authority_signals=(
                qualification.authority_signals
            ),

            content_signals=(
                qualification.content_signals
            ),

            commercial_signals=(
                qualification.commercial_signals
            ),

            evidence=(
                qualification.evidence
            ),

            exclusion_reason=(
                qualification.exclusion_reason
            ),
        )