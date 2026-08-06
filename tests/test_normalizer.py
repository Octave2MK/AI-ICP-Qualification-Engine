from app.acquisition.acquisition_models import ProspectCandidate

from app.acquisition.normalizer import URLNormalizer



def test_linkedin_url_normalization():

    normalizer = URLNormalizer()


    url = ProspectCandidate(
        url=(
            "linkedin.com/"
            "in/John-Doe/?trk=profile"
        )
    )


    result = normalizer.normalize(url)


    assert (
        result.url ==
        "linkedin.com/in/john-doe"
    )