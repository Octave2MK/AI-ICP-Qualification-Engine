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


def test_extract_rejects_spoofed_host_containing_pattern_in_path():
    """Une URL dont l'hôte n'est pas linkedin.com mais dont le chemin
    contient la sous-chaîne "linkedin.com/in/" ne doit pas être acceptée
    (protection contre une usurpation utilisée pour un SSRF)."""

    extractor = URLExtractor()

    results = [
        SearchResult(
            title="Spoofed",
            url="https://evil.example.com/linkedin.com/in/john-doe",
            snippet="",
        ),
    ]

    urls = extractor.extract(results)

    assert urls == []


def test_extract_rejects_host_with_linkedin_com_as_suffix_of_another_domain():
    """Un hôte comme "linkedin.com.evil.com" n'est pas un sous-domaine de
    linkedin.com (son hôte réel est evil.com) et doit être rejeté."""

    extractor = URLExtractor()

    results = [
        SearchResult(
            title="Fake subdomain",
            url="https://linkedin.com.evil.com/in/john-doe",
            snippet="",
        ),
    ]

    urls = extractor.extract(results)

    assert urls == []


def test_extract_accepts_linkedin_country_subdomain():
    """LinkedIn sert des URLs de profil sous des sous-domaines pays
    légitimes (ex. fr.linkedin.com) qui doivent rester acceptés."""

    extractor = URLExtractor()

    results = [
        SearchResult(
            title="Pascal BENVENISTE - Business Coach",
            url="https://fr.linkedin.com/in/benveniste-pascal",
            snippet="",
        ),
    ]

    urls = extractor.extract(results)

    assert len(urls) == 1


def test_extract_accepts_bare_linkedin_host():
    extractor = URLExtractor()

    results = [
        SearchResult(
            title="John Doe",
            url="https://linkedin.com/in/john-doe",
            snippet="",
        ),
    ]

    urls = extractor.extract(results)

    assert len(urls) == 1
