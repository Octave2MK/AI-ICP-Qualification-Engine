from dataclasses import dataclass, field
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/icp.db")


@dataclass(frozen=True)
class Settings:
    """Configuration globale de l'application."""

    REQUEST_TIMEOUT: int = 10

    SEARCH_PROVIDER: str = os.getenv("SEARCH_PROVIDER", "searxng")
    SEARXNG_BASE_URL: str = os.getenv("SEARXNG_BASE_URL", "http://localhost:8080")
    SEARXNG_TIMEOUT: int = int(os.getenv("SEARXNG_TIMEOUT", "30"))
    SEARCH_RETRY_ATTEMPTS: int = int(os.getenv("SEARCH_RETRY_ATTEMPTS", "3"))
    SEARCH_RETRY_DELAY: float = float(os.getenv("SEARCH_RETRY_DELAY", "1"))
    SEARCH_RATE_LIMIT_INTERVAL: float = float(os.getenv("SEARCH_RATE_LIMIT_INTERVAL", "1"))

    TAVILY_API_KEY: str = field(default=os.getenv("TAVILY_API_KEY", ""), repr=False)
    TAVILY_TIMEOUT: int = int(os.getenv("TAVILY_TIMEOUT", "15"))
    TAVILY_MAX_RESULTS: int = int(os.getenv("TAVILY_MAX_RESULTS", "20"))

    SERPAPI_API_KEY: str = field(default=os.getenv("SERPAPI_API_KEY", ""), repr=False)
    SERPAPI_TIMEOUT: int = int(os.getenv("SERPAPI_TIMEOUT", "15"))
    SERPAPI_MAX_RESULTS: int = int(os.getenv("SERPAPI_MAX_RESULTS", "20"))

    PAGE_FETCHER_USER_AGENT: str = field(
        default_factory=lambda: os.getenv(
            "PAGE_FETCHER_USER_AGENT",
            "AI-ICP-Qualification-Engine/1.0",
        )
    )
    # Backward-compatible public setting kept for existing callers/tests.
    USER_AGENT: str = field(
        default_factory=lambda: os.getenv(
            "PAGE_FETCHER_USER_AGENT",
            "AI-ICP-Qualification-Engine/1.0",
        )
    )
    PAGE_FETCHER_TIMEOUT: int = field(
        default_factory=lambda: int(os.getenv("PAGE_FETCHER_TIMEOUT", "10"))
    )
    PAGE_FETCHER_RETRY_ATTEMPTS: int = field(
        default_factory=lambda: int(os.getenv("PAGE_FETCHER_RETRY_ATTEMPTS", "2"))
    )
    PAGE_FETCHER_BACKOFF_SECONDS: float = field(
        default_factory=lambda: float(os.getenv("PAGE_FETCHER_BACKOFF_SECONDS", "2"))
    )
    PAGE_FETCHER_DELAY_SECONDS: float = field(
        default_factory=lambda: float(os.getenv("PAGE_FETCHER_DELAY_SECONDS", "1"))
    )

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = field(default=os.getenv("GEMINI_API_KEY", ""), repr=False)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    # Nombre max de profils regroupés dans un même appel LLM batch. Un lot
    # unique trop volumineux (jusqu'à max_prospects=100) augmente le rayon
    # d'explosion en cas d'échec (tout le lot repart en erreur) et la taille
    # du prompt envoyé. Découper en sous-lots limite les deux sans perdre
    # l'essentiel du gain par rapport à un appel par profil.
    GEMINI_BATCH_SIZE: int = int(os.getenv("GEMINI_BATCH_SIZE", "15"))
    OPENAI_API_KEY: str = field(default=os.getenv("OPENAI_API_KEY", ""), repr=False)

    WORKFLOW_COOLDOWN_SECONDS: float = float(os.getenv("WORKFLOW_COOLDOWN_SECONDS", "30"))
    MAX_WORKFLOW_RUNS_PER_SESSION: int = int(os.getenv("MAX_WORKFLOW_RUNS_PER_SESSION", "20"))

    ENRICHMENT_ENGINE: str = os.getenv("ENRICHMENT_ENGINE", "bs4")


settings = Settings()