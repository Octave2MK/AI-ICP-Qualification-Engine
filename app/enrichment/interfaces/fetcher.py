from abc import ABC, abstractmethod


class BaseFetcher(ABC):
    """Contrat pour tous les fetchers."""

    @abstractmethod
    def fetch(self, url: str) -> str:
        """Retourne le HTML d'une page."""
        raise NotImplementedError