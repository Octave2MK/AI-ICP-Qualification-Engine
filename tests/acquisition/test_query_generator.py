from app.acquisition.acquisition_models import ICP
from app.acquisition.query_generator import QueryGenerator


def test_query_generator_keeps_original_exact_query():
    icp = ICP(
        job_titles=["Business Coach"],
        countries=["France"],
    )

    queries = QueryGenerator().generate(icp)
    texts = [query.text for query in queries]

    assert 'site:linkedin.com/in "Business Coach" "France"' in texts


def test_query_generator_adds_broader_country_variant():
    icp = ICP(
        job_titles=["Business Coach"],
        countries=["France"],
    )

    queries = QueryGenerator().generate(icp)
    texts = [query.text for query in queries]

    assert 'site:linkedin.com/in "Business Coach" France' in texts


def test_query_generator_uses_only_one_keyword_variant():
    icp = ICP(
        job_titles=["Business Coach"],
        countries=["France"],
        keywords=["entrepreneur", "dirigeant", "B2B"],
    )

    queries = QueryGenerator().generate(icp)
    texts = [query.text for query in queries]

    assert (
        'site:linkedin.com/in "Business Coach" "entrepreneur" France'
        in texts
    )
    assert not any('"dirigeant"' in text for text in texts)
    assert not any('"B2B"' in text for text in texts)


def test_query_generator_deduplicates_keyword_sources():
    icp = ICP(
        job_titles=["Business Coach"],
        countries=["France"],
        keywords=["Entrepreneur"],
        required_keywords=["entrepreneur"],
    )

    queries = QueryGenerator().generate(icp)
    texts = [query.text for query in queries]

    assert len(texts) == len(set(texts))
    assert texts.count(
        'site:linkedin.com/in "Business Coach" "Entrepreneur" France'
    ) == 1
