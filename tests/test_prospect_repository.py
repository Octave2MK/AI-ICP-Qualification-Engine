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



def test_create_if_not_exists_refreshes_stale_fullname_and_job_title(db_session):

    repository = ProspectRepository()

    prospect1 = Prospect(
        fullname="Unknown",
        linkedin_url="linkedin.com/in/john-doe",
        job_title="",
    )

    first = repository.create_if_not_exists(
        db_session,
        prospect1,
    )

    # Un run ultérieur retrouve le même prospect (recherche déterministe
    # côté API) avec des données fraîches, cette fois exploitables.
    prospect2 = Prospect(
        fullname="John Doe",
        linkedin_url="linkedin.com/in/john-doe",
        job_title="Business Coach",
    )

    second = repository.create_if_not_exists(
        db_session,
        prospect2,
    )

    assert first.id == second.id
    assert second.fullname == "John Doe"
    assert second.job_title == "Business Coach"


def test_create_if_not_exists_does_not_overwrite_with_empty_values(db_session):

    repository = ProspectRepository()

    prospect1 = Prospect(
        fullname="John Doe",
        linkedin_url="linkedin.com/in/john-doe",
        job_title="Business Coach",
    )

    first = repository.create_if_not_exists(
        db_session,
        prospect1,
    )

    # Un run ultérieur ne doit jamais écraser une donnée déjà correcte
    # avec une valeur vide.
    prospect2 = Prospect(
        fullname="",
        linkedin_url="linkedin.com/in/john-doe",
        job_title="",
    )

    second = repository.create_if_not_exists(
        db_session,
        prospect2,
    )

    assert first.id == second.id
    assert second.fullname == "John Doe"
    assert second.job_title == "Business Coach"