from app.acquisition.acquisition_models import ProspectCandidate
from app.acquisition.prospect_mapper import ProspectMapper


def test_map_url_to_prospect():
    mapper = ProspectMapper()

    candidate = ProspectCandidate(
        url="linkedin.com/in/john-doe"
    )

    prospect = mapper.map(candidate)

    assert prospect.linkedin_url == "linkedin.com/in/john-doe"
    assert prospect.fullname == "Unknown"
    assert prospect.job_title == ""


def test_map_extracts_name_and_job_title_from_linkedin_result_title():
    mapper = ProspectMapper()

    candidate = ProspectCandidate(
        url="https://linkedin.com/in/pascal-benveniste",
        title="Pascal BENVENISTE - Business Coach. Accompagnement des dirigeants - LinkedIn",
        snippet="Business Coach. Accompagnement des dirigeants vers leur plein potentiel.",
    )

    prospect = mapper.map(candidate)

    assert prospect.fullname == "Pascal BENVENISTE"
    assert prospect.job_title == "Business Coach. Accompagnement des dirigeants"
    assert prospect.linkedin_url == "https://linkedin.com/in/pascal-benveniste"


def test_map_extracts_job_title_before_pipe():
    mapper = ProspectMapper()

    candidate = ProspectCandidate(
        url="https://linkedin.com/in/eric-mallet",
        title="Eric Mallet - Executive Business Coach | J'accompagne dirigeants et managers - LinkedIn",
    )

    prospect = mapper.map(candidate)

    assert prospect.fullname == "Eric Mallet"
    assert prospect.job_title == "Executive Business Coach"


def test_map_keeps_job_title_with_internal_hyphens():
    mapper = ProspectMapper()

    candidate = ProspectCandidate(
        url="https://linkedin.com/in/test",
        title="Jean Dupont - Business Coach - Stratégie d'entreprise et pilotage - LinkedIn",
    )

    prospect = mapper.map(candidate)

    assert prospect.fullname == "Jean Dupont"
    assert prospect.job_title == "Business Coach - Stratégie d'entreprise et pilotage"
