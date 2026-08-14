from app.factory import create_full_workflow
from app.database.database import (
    SessionLocal,
    Base,
    engine,
)
from app.database.schema import ensure_schema

# Import des modèles afin que toutes les tables soient enregistrées
# dans Base.metadata avant create_all().
import app.database.models  # noqa: F401


def run_workflow(
        icp,
        progress_callback=None,
):
    # Garantit qu'une base fraîche possède également la table
    # qualifications et applique les migrations additives nécessaires
    # aux bases déjà existantes.
    Base.metadata.create_all(bind=engine)
    ensure_schema()

    db = SessionLocal()

    try:
        workflow = create_full_workflow(db)
        results = workflow.run(
            db=db,
            icp=icp,
            progress_callback=progress_callback,
        )
        return results
    finally:
        db.close()
