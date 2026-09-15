from sqlalchemy.orm import Session

from app.database.models import Prospect


class ProspectRepository:
    """
    Gestion de la persistance des prospects.
    """
    def create(
        self,
        db: Session,
        prospect: Prospect,
    ) -> Prospect:

        db.add(prospect)
        db.commit()
        db.refresh(prospect)

        return prospect

    def get_by_linkedin_url(
        self,
        db: Session,
        linkedin_url: str,
    ) -> Prospect | None:

        return (
            db.query(Prospect)
            .filter(
                Prospect.linkedin_url == linkedin_url
            )
            .first()
        )

    def create_if_not_exists(
        self,
        db: Session,
        prospect: Prospect,
    ) -> Prospect:

        existing = self.get_by_linkedin_url(
            db,
            prospect.linkedin_url,
        )

        if existing:
            # Un même prospect peut être retrouvé lors de runs successifs
            # (recherche déterministe côté Tavily/SerpApi). La ligne
            # existante peut avoir été créée par une version antérieure du
            # pipeline, avec un fullname/job_title vide ou obsolète — la
            # renvoyer telle quelle empêcherait le fallback d'acquisition
            # de jamais fonctionner pour ce prospect, quel que soit le
            # nombre de corrections apportées depuis.
            updated = False

            if prospect.fullname and prospect.fullname != existing.fullname:
                existing.fullname = prospect.fullname
                updated = True

            if prospect.job_title and prospect.job_title != existing.job_title:
                existing.job_title = prospect.job_title
                updated = True

            if updated:
                db.commit()
                db.refresh(existing)

            return existing

        return self.create(
            db,
            prospect,
        )