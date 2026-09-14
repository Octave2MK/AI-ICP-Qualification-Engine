from app.acquisition.acquisition_models import ICP
from app.acquisition.query_generator import QueryGenerator


def test_query_generator_keeps_original_exact_query():
    icp = ICP(job_titles=["Business Coach"], countries=["France"])
    texts = [query.text for query in QueryGenerator().generate(icp)]
    assert 'site:linkedin.com/in "Business Coach" "France"' in texts


def test_query_generator_adds_non_site_variant():
    icp = ICP(job_titles=["Business Coach"], countries=["France"])
    texts = [query.text for query in QueryGenerator().generate(icp)]
    assert '"Business Coach" France linkedin.com/in' in texts


def test_query_generator_uses_up_to_three_semantic_keywords():
    icp = ICP(
        job_titles=["Business Coach"],
        countries=["France"],
        keywords=["entrepreneur", "dirigeant", "B2B", "marketing"],
    )
    texts = [query.text for query in QueryGenerator().generate(icp)]

    assert 'site:linkedin.com/in "Business Coach" "entrepreneur" France' in texts
    assert 'site:linkedin.com/in "Business Coach" "dirigeant" France' in texts
    assert 'site:linkedin.com/in "Business Coach" "B2B" France' in texts
    assert not any('"marketing"' in text for text in texts)


def test_query_generator_deduplicates_keyword_sources_case_insensitively():
    icp = ICP(
        job_titles=["Business Coach"],
        countries=["France"],
        keywords=["Entrepreneur", "Dirigeant"],
        required_keywords=["entrepreneur", "B2B"],
    )
    texts = [query.text for query in QueryGenerator().generate(icp)]

    assert len(texts) == len(set(texts))
    assert sum('"Entrepreneur"' in text for text in texts) == 1
    assert sum('"B2B"' in text for text in texts) == 1


def test_query_generator_avoids_cosmetic_variants():
    icp = ICP(job_titles=["Business Coach"], countries=["France"])
    texts = [query.text for query in QueryGenerator().generate(icp)]

    assert 'site:linkedin.com/in "Business Coach" France' not in texts
    assert '"Business Coach" France linkedin' not in texts
