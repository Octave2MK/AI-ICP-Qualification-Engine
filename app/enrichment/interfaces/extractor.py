from abc import ABC, abstractmethod

from app.enrichment.dto import ProfileData


class BaseExtractor(ABC):
    """Contrat pour tous les extracteurs de profils."""

    @abstractmethod
    def extract(self, html: str, linkedin_url: str) -> ProfileData:
        """Extrait les informations d'un profil."""
        raise NotImplementedError