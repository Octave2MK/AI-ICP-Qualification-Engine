from app.database.models import Prospect
from app.repositories.qualification_repository import QualificationRepository
from app.qualification.dto import QualificationResult


def test_save_qualification(db_session):

    prospect = Prospect(
        fullname="Jean Dupont",
        linkedin_url="https://linkedin.com/in/jean",
        country="France",
        job_title="Business Coach",
    )

    db_session.add(prospect)
    db_session.commit()
    db_session.refresh(prospect)


    result = QualificationResult(
        profession="Business Coach",
        sector="Coaching",
        target_market="B2B",

        offer_detected=True,

        authority_signals=[
            "Conférences"
        ],

        content_signals=[
            "Posts LinkedIn"
        ],

        commercial_signals=[
            "Programme premium"
        ],

        icp_match=True,

        confidence=0.9,

        evidence=[
            "Accompagnement PME"
        ],

        exclusion_reason=None,
    )


    repository = QualificationRepository()


    qualification = repository.save(
        db_session,
        prospect.id,
        result,
    )


    assert qualification.id is not None

    assert qualification.prospect_id == prospect.id

    assert qualification.profession == "Business Coach"

    assert qualification.icp_match == 1

    assert qualification.offer_detected == 1

    assert qualification.confidence == 0.9