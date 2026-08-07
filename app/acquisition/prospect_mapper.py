from app.acquisition.acquisition_models import ProspectCandidate
from app.database.models import Prospect


class ProspectMapper:
    """
    Transforme une URL OSINT en Prospect SQLAlchemy.
    """
    def _extract_name(self, title: str) -> str:
        if not title:
            return "Unknown"

        name = title.split("-")[0].strip()

        name = name.replace("| LinkedIn", "").strip()

        return name or "Unknown"


    def _extract_job_title(self, title: str) -> str | None:
        if "-" not in title:
            return None

        job = title.split("-", 1)[1]

        job = job.split("|")[0]

        return job.strip() or None


    def map(
        self,
        candidate
    ):

        return Prospect(
            linkedin_url=candidate.url,
            fullname=candidate.title or "Unknown",
            job_title=candidate.snippet or "",
        )