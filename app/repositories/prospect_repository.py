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
            return existing
        return self.create(
            db,
            prospect,
        )