from abc import ABC, abstractmethod

from app.enrichment.dto import ProfileData


class BaseBatchEnricher(ABC):
    """Contrat pour un enrichissement de profils en lot (par opposition au
    contrat BaseFetcher/BaseExtractor, pensé pour une URL à la fois)."""

    @abstractmethod
    def enrich_many(self, linkedin_urls: list[str]) -> dict[str, ProfileData]:
        """Enrichit un lot d'URLs LinkedIn en une seule opération.

        Retourne un dict associant chaque URL enrichie avec succès à son
        ProfileData. Une URL absente du résultat signifie un échec pour
        cette URL précise ; l'appelant doit traiter cela comme une entrée
        d'erreur pour le prospect concerné, sans faire échouer le lot
        entier."""
        raise NotImplementedError
