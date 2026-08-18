from app.factory import create_full_workflow
from app.database.database import SessionLocal, init_db


def run_workflow(
        icp,
        progress_callback=None,
):
    # Garantit qu'une base fraîche possède également la table
    # qualifications et applique les migrations additives nécessaires
    # aux bases déjà existantes.
    init_db()

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
