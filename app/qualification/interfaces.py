from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def analyze(self, text: str) -> str:
        """
        Analyse un texte et retourne une réponse JSON sous forme de chaîne.
        """
        raise NotImplementedError

    def analyze_batch(self, texts: list[str]) -> list[str]:
        """
        Analyse plusieurs prompts.

        Implémentation de compatibilité : les LLM qui ne supportent pas
        nativement le batch retombent sur l'analyse individuelle.
        Les clients capables de batcher doivent surcharger cette méthode.
        """
        return [self.analyze(text) for text in texts]
