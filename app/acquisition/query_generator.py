from app.acquisition.acquisition_models import ICP, SearchQuery


class QueryGenerator:
    """
    Génère des requêtes Google à partir d'un ICP.
    """

    BASE_QUERY = "site:linkedin.com/in"

    def generate(self, icp: ICP) -> list[SearchQuery]:
        queries: list[SearchQuery] = []

        for title in icp.job_titles:
            for country in icp.countries:

                query = (
                    f'{self.BASE_QUERY} '
                    f'"{title}" '
                    f'"{country}"'
                )

                queries.append(
                    SearchQuery(text=query)
                )

        return queries