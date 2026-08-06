from abc import ABC, abstractmethod

from app.acquisition.acquisition_models import (
    SearchQuery,
    SearchResult,
)


class SearchProvider(ABC):
    """
    Interface de tous les moteurs de recherche.
    """

    @abstractmethod
    def search(
        self,
        query: SearchQuery
    ) -> list[SearchResult]:
        """
        Exécute une recherche.
        """
        raise NotImplementedError

class MockSearchProvider(SearchProvider):
    """
    Fournisseur fictif utilisé pour les tests.
    """

    def search(
        self,
        query: SearchQuery
    ) -> list[SearchResult]:

        return [
            SearchResult(
                title="John Doe",
                url="https://www.linkedin.com/in/john-doe",
                snippet="Business Coach"
            ),
            SearchResult(
                title="Jane Smith",
                url="https://www.linkedin.com/in/jane-smith",
                snippet="Sales Coach"
            ),
        ]