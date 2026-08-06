from app.acquisition.acquisition_models import ProspectCandidate

from app.acquisition.prospect_mapper import ProspectMapper



def test_map_url_to_prospect():


    mapper = ProspectMapper()


    url = ProspectCandidate(
        url="linkedin.com/in/john-doe"
    )


    prospect = mapper.map(url)


    assert prospect.linkedin_url == (
        "linkedin.com/in/john-doe"
    )

    assert prospect.fullname == "Unknown"

    assert prospect.linkedin_url == (
        "linkedin.com/in/john-doe"
    )