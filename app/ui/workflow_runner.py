from app.factory import create_full_workflow
from app.database.database import SessionLocal


def run_workflow(
        icp,
        progress_callback=None,
):
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