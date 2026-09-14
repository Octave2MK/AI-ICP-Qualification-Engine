from app.acquisition.acquisition_models import ICP, SearchQuery


class QueryGenerator:
    """Génère des requêtes de recherche diversifiées sans variantes cosmétiques."""

    BASE_QUERY = "site:linkedin.com/in"
    MAX_KEYWORD_VARIANTS = 3

    def generate(self, icp: ICP) -> list[SearchQuery]:
        queries: list[SearchQuery] = []
        seen: set[str] = set()
        keywords = self._get_search_keywords(icp)

        for title in icp.job_titles:
            for country in icp.countries:
                # Deux formulations de base seulement : elles couvrent les
                # moteurs qui gèrent correctement site: et ceux qui le gèrent mal.
                self._add_query(
                    queries,
                    seen,
                    f'{self.BASE_QUERY} "{title}" "{country}"',
                )
                self._add_query(
                    queries,
                    seen,
                    f'"{title}" {country} linkedin.com/in',
                )

                # Diversification sémantique contrôlée via les mots-clés ICP.
                # Chaque terme apporte un signal de recherche différent, au lieu
                # de payer plusieurs variantes syntaxiques presque identiques.
                for keyword in keywords[: self.MAX_KEYWORD_VARIANTS]:
                    self._add_query(
                        queries,
                        seen,
                        f'{self.BASE_QUERY} "{title}" "{keyword}" {country}',
                    )

        return queries

    @staticmethod
    def _get_search_keywords(icp: ICP) -> list[str]:
        keywords: list[str] = []

        for keyword in [*icp.keywords, *icp.required_keywords]:
            normalized = keyword.strip()
            if normalized and normalized.lower() not in {
                existing.lower() for existing in keywords
            }:
                keywords.append(normalized)

        return keywords

    @staticmethod
    def _add_query(
        queries: list[SearchQuery],
        seen: set[str],
        text: str,
    ) -> None:
        text = text.strip()
        if not text or text in seen:
            return
        seen.add(text)
        queries.append(SearchQuery(text=text))
