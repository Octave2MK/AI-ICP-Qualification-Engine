from app.acquisition.acquisition_models import ProspectCandidate

from app.acquisition.deduplicator import Deduplicator



def test_remove_duplicates():

    deduplicator = Deduplicator()


    urls = [

        ProspectCandidate(
            url="linkedin.com/in/john-doe"
        ),

        ProspectCandidate(
            url="linkedin.com/in/john-doe"
        ),

        ProspectCandidate(
            url="linkedin.com/in/jane-smith"
        )

    ]


    result = deduplicator.deduplicate(urls)


    assert len(result) == 2


    assert result[0].url == (
        "linkedin.com/in/john-doe"
    )


    assert result[1].url == (
        "linkedin.com/in/jane-smith"
    )