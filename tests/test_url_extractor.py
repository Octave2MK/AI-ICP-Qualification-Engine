from app.acquisition.acquisition_models import SearchResult

from app.acquisition.url_extractor import URLExtractor



def test_extract_linkedin_profiles():

    extractor = URLExtractor()


    results = [

        SearchResult(
            title="John Doe",
            url="https://www.linkedin.com/in/john-doe",
            snippet="Business Coach"
        ),


        SearchResult(
            title="OpenAI",
            url="https://www.linkedin.com/company/openai",
            snippet="Company"
        ),


        SearchResult(
            title="Random",
            url="https://example.com/page",
            snippet=""
        )

    ]


    urls = extractor.extract(results)


    assert len(urls) == 1

    assert (
        urls[0].url ==
        "https://www.linkedin.com/in/john-doe"
    )