from app.acquisition.acquisition_models import ICP
from app.acquisition.query_generator import QueryGenerator


def test_generate_queries():

    generator = QueryGenerator()

    icp = ICP(
        job_titles=["Business Coach"],
        countries=["France"]
    )

    queries = generator.generate(icp)

    assert len(queries) == 1
    assert queries[0].text == (
        'site:linkedin.com/in '
        '"Business Coach" '
        '"France"'
    )

    def test_multiple_queries():
        generator = QueryGenerator()

        icp = ICP(
            job_titles=[
                "Business Coach",
                "Sales Coach"
            ],
            countries=[
                "France",
                "Belgique"
            ]
        )

        queries = generator.generate(icp)

        assert len(queries) == 4