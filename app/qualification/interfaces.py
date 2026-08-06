from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    def analyze(self, text: str) -> str:
        """
        Analyse un texte et retourne une réponse JSON sous forme de chaîne.
        """
        raise NotImplementedError