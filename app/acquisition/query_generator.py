from app.acquisition.acquisition_models import ICP, SearchQuery


class QueryGenerator:
    """
    Génère des requêtes de recherche à partir d'un ICP.

    Une seule formulation de requête est trop fragile pour les moteurs
    métamoteurs : certains moteurs interprètent différemment les opérateurs
    `site:` et les guillemets. Le générateur conserve donc la requête exacte
    historique et ajoute quelques variantes contrôlées afin d'améliorer le
    rappel sans multiplier inutilement les appels réseau.

    Constat terrain (SearXNG, moteurs bing/duckduckgo) : l'opérateur `site:`
    n'est pas toujours transmis correctement par l'adaptateur SearXNG vers
    le moteur sous-jacent. Les variantes sans `site:` donnent donc au moteur
    des signaux textuels explicites (`linkedin.com/in`) et laissent ensuite
    le pipeline vérifier l'URL réelle avant de qualifier un résultat.
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

                self._add_query(
                    queries,
                    seen,
                    f'{self.BASE_QUERY} "{title}" {country}',
                )

                # Variante indépendante de l'opérateur site:. Le domaine
                # et le chemin LinkedIn sont conservés comme texte explicite
                # afin d'aider les moteurs qui ignorent les opérateurs.
                self._add_query(
                    queries,
                    seen,
                    f'"{title}" {country} linkedin.com/in',
                )

                # Variante plus générale conservée en complément : certains
                # moteurs classent mieux les profils lorsque "linkedin" est
                # utilisé comme terme simple plutôt que comme chemin.
                self._add_query(
                    queries,
                    seen,
                    f'"{title}" {country} linkedin',
                )

                for keyword in keywords[: self.MAX_KEYWORD_VARIANTS]:
                    self._add_query(
                        queries,
                        seen,
                        f'{self.BASE_QUERY} "{title}" "{keyword}" {country}',
                    )

                    # Même variante enrichie sans dépendre de site:.
                    self._add_query(
                        queries,
                        seen,
                        f'"{title}" "{keyword}" {country} linkedin.com/in',
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
