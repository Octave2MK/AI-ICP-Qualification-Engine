from app.enrichment.dto import ProfileData


def test_is_empty_true_when_no_identity_or_bio_content():
    profile = ProfileData(
        linkedin_url="linkedin.com/in/john-doe",
        name="",
        headline="",
        about="",
        raw_text="Identifiez-vous pour voir le profil complet de John",
    )

    assert profile.is_empty() is True


def test_is_empty_false_when_name_present():
    profile = ProfileData(
        linkedin_url="linkedin.com/in/john-doe",
        name="John Doe",
        headline="",
        about="",
        raw_text="",
    )

    assert profile.is_empty() is False


def test_is_empty_false_when_headline_present():
    profile = ProfileData(
        linkedin_url="linkedin.com/in/john-doe",
        name="",
        headline="Business Coach",
        about="",
        raw_text="",
    )

    assert profile.is_empty() is False


def test_is_empty_false_when_about_present():
    profile = ProfileData(
        linkedin_url="linkedin.com/in/john-doe",
        name="",
        headline="",
        about="J'aide les entrepreneurs à développer leur activité.",
        raw_text="",
    )

    assert profile.is_empty() is False