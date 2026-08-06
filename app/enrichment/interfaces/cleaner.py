from abc import ABC, abstractmethod


class BaseCleaner(ABC):
    """Contrat pour tous les nettoyeurs de texte."""

    @abstractmethod
    def clean(self, text: str) -> str:
        raise NotImplementedError