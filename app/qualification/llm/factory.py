from app.core.settings import settings
from app.exceptions.configuration_error import ConfigurationError
from app.qualification.llm.fake_llm import FakeLLM
from app.qualification.llm.gemini_client import GeminiClient


class LLMFactory:
    @staticmethod
    def create(provider: str | None = None):
        """
        Crée le fournisseur LLM demandé.

        Si aucun provider n'est fourni, utilise celui défini
        dans la configuration.
        """
        provider = provider or settings.LLM_PROVIDER

        provider = provider.lower()

        if provider == "fake":
            return FakeLLM()

        if provider == "gemini":
            if not settings.GEMINI_API_KEY:
                raise ConfigurationError(
                    "GEMINI_API_KEY is not configured. Set it in .env "
                    "before using LLM_PROVIDER=gemini."
                )
            return GeminiClient(
                api_key=settings.GEMINI_API_KEY,
                model=settings.GEMINI_MODEL,
            )

        if provider == "openai":
            raise NotImplementedError(
                "OpenAIClient n'est pas encore implémenté."
            )

        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )