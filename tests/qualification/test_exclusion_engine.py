from app.enrichment.dto import ProfileData
from app.qualification.exclusions.exclusion_engine import ExclusionEngine


def test_exclude_student_profile():

    profile = ProfileData(
        linkedin_url="",
        name="Jean",
        headline="Étudiant en marketing",
        about="Recherche un stage",
        raw_text="Student internship",
        clean_text="",
    )


    result = ExclusionEngine.check(profile)


    assert result["excluded"] is True

    assert result["reason"] == "Profil étudiant"



def test_accept_business_coach():

    profile = ProfileData(
        linkedin_url="",
        name="Jean",
        headline="Business Coach indépendant",
        about="J'accompagne les PME",
        raw_text="Coaching B2B",
        clean_text="",
    )


    result = ExclusionEngine.check(profile)


    assert result["excluded"] is False

    assert result["reason"] is None