from app.acquisition.acquisition_models import ICP, SearchQuery


class QueryGenerator:
    """
    Génère des requêtes de recherche à partir d'un ICP.

    Une seule formulation de requête est trop fragile pour les moteurs
    métamoteurs : certains moteurs interprètent différemment les opérateurs
    `site:` et les guillemets. Le générateur conserve donc la requête exacte
    historique et ajoute quelques variantes contrôlées afin d'améliorer le
    rappel sans multiplier inutilement les appels réseau.
    """

    BASE_QUERY = "site:linkedin.com/in"
    MAX_KEYWORD_VARIANTS = 1

    def generate(self, icp: ICP) -> list[SearchQuery]:
        queries: list[SearchQuery] = []
        seen: set[str] = set()

        keywords = self._get_search_keywords(icp)

        for title in icp.job_titles:
            for country in icp.countries:
                self._add_query(
                    queries,
                    seen,
                    f'{self.BASE_QUERY} "{title}" "{country}"',
                )

                # Variante plus souple : le pays n'est pas entre guillemets.
                self._add_query(
                    queries,
                    seen,
                    f'{self.BASE_QUERY} "{title}" {country}',
                )

                # Une seule variante enrichie pour éviter une explosion du
                # nombre d'appels lorsque l'utilisateur fournit beaucoup de
                # mots-clés dans son ICP.
                for keyword in keywords[: self.MAX_KEYWORD_VARIANTS]:
                    self._add_query(
                        queries,
                        seen,
                        f'{self.BASE_QUERY} "{title}" "{keyword}" {country}',
                    )

        return queries

    @staticmethod
    def _get_search_keywords(icp: ICP) -> list[str]:
        """
        Retourne des mots-clés utiles à la recherche sans dupliquer les termes.

        `keywords` reste prioritaire car il représente les termes de recherche
        facultatifs. `required_keywords` complète la recherche lorsqu'aucun
        mot-clé facultatif n'est fourni.
        """
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
