import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.database import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db_session():

    Base.metadata.create_all(
        bind=engine
    )


    session = TestingSessionLocal()


    try:
        yield session

    finally:
        session.close()


        Base.metadata.drop_all(
            bind=engine
        )