from app.acquisition.acquisition_models import ProspectCandidate
from app.database.models import Prospect


class ProspectMapper:
    """
    Transforme un résultat de recherche OSINT en Prospect SQLAlchemy.

    Les résultats de moteurs de recherche utilisent généralement un titre
    du type : "Nom - Métier | LinkedIn". Le mapper sépare explicitement
    le nom et le métier au lieu de stocker le titre/snippet brut.
    """

    def _extract_name(self, title: str) -> str:
        if not title:
            return "Unknown"

        name = title.split(" - ", 1)[0].strip()
        name = name.replace("| LinkedIn", "").strip()

        return name or "Unknown"

    def _extract_job_title(self, title: str) -> str | None:
        if not title or " - " not in title:
            return None

        job = title.split(" - ", 1)[1].strip()
        job = job.replace("| LinkedIn", "").strip()

        # Les résultats LinkedIn peuvent utiliser " - LinkedIn" comme
        # suffixe final. Il faut le retirer sans supprimer les tirets
        # légitimes présents dans l'intitulé du métier.
        if job.endswith(" - LinkedIn"):
            job = job[: -len(" - LinkedIn")].strip()

        # Un titre peut également contenir "| LinkedIn" après le métier.
        job = job.split("|", 1)[0].strip()

        return job or None

    def map(
        self,
        candidate: ProspectCandidate,
    ) -> Prospect:
        return Prospect(
            linkedin_url=candidate.url,
            fullname=self._extract_name(candidate.title),
            job_title=self._extract_job_title(candidate.title) or "",
        )
