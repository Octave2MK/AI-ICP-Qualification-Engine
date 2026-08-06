from app.qualification.normalization.profession_normalizer import (
    ProfessionNormalizer,
)


def test_normalize_business_coach():
    assert (
        ProfessionNormalizer.normalize("Coach Business")
        == "Business Coach"
    )


def test_normalize_business_coach_2():
    assert (
        ProfessionNormalizer.normalize("Coach de dirigeants")
        == "Business Coach"
    )


def test_unknown_profession():
    assert (
        ProfessionNormalizer.normalize("Architecte")
        == "Architecte"
    )