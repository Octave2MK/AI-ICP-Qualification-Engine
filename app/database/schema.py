from sqlalchemy import inspect, text

from app.database.database import engine


def ensure_schema():
    """Apply small additive schema changes to an existing database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "qualifications" not in tables:
        return

    columns = {
        column["name"]
        for column in inspector.get_columns("qualifications")
    }

    if "icp_fingerprint" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE qualifications "
                    "ADD COLUMN icp_fingerprint VARCHAR"
                )
            )

        # Index creation is deliberately separate so the migration remains
        # compatible with existing SQLite databases.
        with engine.begin() as connection:
            connection.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS "
                    "ix_qualifications_icp_fingerprint "
                    "ON qualifications (icp_fingerprint)"
                )
            )
