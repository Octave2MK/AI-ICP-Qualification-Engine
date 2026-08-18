import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool

from app.database import schema


@pytest.fixture
def isolated_engine(monkeypatch):
    """A dedicated in-memory SQLite engine, isolated from the app's real
    engine and from other tests, with a single shared connection so tables
    created in one statement remain visible to the next (default SQLite
    in-memory behavior otherwise creates a fresh DB per connection).
    Disposed after the test to avoid leaking the underlying connection."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    monkeypatch.setattr(schema, "engine", engine)
    try:
        yield engine
    finally:
        engine.dispose()


def test_ensure_schema_is_a_noop_when_qualifications_table_is_missing(
    isolated_engine,
):
    # Should not raise even though no tables exist at all.
    schema.ensure_schema()

    inspector = inspect(isolated_engine)
    assert "qualifications" not in inspector.get_table_names()


def test_ensure_schema_adds_missing_icp_fingerprint_column(isolated_engine):
    with isolated_engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE qualifications ("
                "id INTEGER PRIMARY KEY, "
                "prospect_id INTEGER NOT NULL"
                ")"
            )
        )

    inspector = inspect(isolated_engine)
    columns_before = {
        column["name"] for column in inspector.get_columns("qualifications")
    }
    assert "icp_fingerprint" not in columns_before

    schema.ensure_schema()

    inspector = inspect(isolated_engine)
    columns_after = {
        column["name"] for column in inspector.get_columns("qualifications")
    }
    assert "icp_fingerprint" in columns_after


def test_ensure_schema_is_idempotent_when_column_already_exists(
    isolated_engine,
):
    with isolated_engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE qualifications ("
                "id INTEGER PRIMARY KEY, "
                "prospect_id INTEGER NOT NULL"
                ")"
            )
        )

    schema.ensure_schema()
    # Calling it again must not raise (e.g. no attempt to re-add the column).
    schema.ensure_schema()

    inspector = inspect(isolated_engine)
    columns = [
        column["name"] for column in inspector.get_columns("qualifications")
    ]
    assert columns.count("icp_fingerprint") == 1
