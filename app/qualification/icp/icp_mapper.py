from app.acquisition.acquisition_models import ICP
from app.qualification.icp.icp_definition import ICPDefinition


class ICPMapper:
    """
    Convertit l'ICP utilisé par le moteur d'acquisition
    en définition ICP utilisée par le moteur de qualification.
    """

    @staticmethod
    def to_definition(
        icp: ICP,
    ) -> ICPDefinition:
        return ICPDefinition(
            professions=list(icp.job_titles),
            sectors=list(icp.sectors),
            target_markets=list(icp.countries),
            required_keywords=list(
                icp.required_keywords
            ),
            forbidden_keywords=list(
                icp.forbidden_keywords
            ),
        )
