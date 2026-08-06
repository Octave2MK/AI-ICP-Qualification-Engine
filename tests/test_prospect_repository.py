from app.database.models import Prospect

from app.repositories.prospect_repository import (
    ProspectRepository
)



def test_create_prospect(db_session):


    repository = ProspectRepository()


    prospect = Prospect(
        fullname="John Doe",
        linkedin_url="linkedin.com/in/john-doe",
        country="France",
        job_title="Business Coach"
    )


    saved = repository.create(
        db_session,
        prospect,
    )


    assert saved.id is not None

    assert saved.fullname == "John Doe"

    assert (
        saved.linkedin_url ==
        "linkedin.com/in/john-doe"
    )



def test_create_if_not_exists(db_session):


    repository = ProspectRepository()


    prospect1 = Prospect(
        fullname="John Doe",
        linkedin_url="linkedin.com/in/john-doe"
    )


    first = repository.create_if_not_exists(
        db_session,
        prospect1,
    )


    prospect2 = Prospect(
        fullname="John Doe Updated",
        linkedin_url="linkedin.com/in/john-doe"
    )


    second = repository.create_if_not_exists(
        db_session,
        prospect2,
    )


    assert first.id == second.id

    assert (
        second.fullname ==
        "John Doe"
    )