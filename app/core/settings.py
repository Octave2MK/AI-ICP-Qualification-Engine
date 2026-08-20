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

    PAGE_FETCHER_USER_AGENT: str = os.getenv(
        "PAGE_FETCHER_USER_AGENT",
        "AI-ICP-Qualification-Engine/1.0",
    )
    PAGE_FETCHER_TIMEOUT: int = int(os.getenv("PAGE_FETCHER_TIMEOUT", "10"))
    PAGE_FETCHER_RETRY_ATTEMPTS: int = int(os.getenv("PAGE_FETCHER_RETRY_ATTEMPTS", "2"))
    PAGE_FETCHER_BACKOFF_SECONDS: float = float(
        os.getenv("PAGE_FETCHER_BACKOFF_SECONDS", "2")
    )
    PAGE_FETCHER_DELAY_SECONDS: float = float(
        os.getenv("PAGE_FETCHER_DELAY_SECONDS", "1")
    )

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = field(default=os.getenv("GEMINI_API_KEY", ""), repr=False)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    OPENAI_API_KEY: str = field(default=os.getenv("OPENAI_API_KEY", ""), repr=False)

    WORKFLOW_COOLDOWN_SECONDS: float = float(os.getenv("WORKFLOW_COOLDOWN_SECONDS", "30"))
    MAX_WORKFLOW_RUNS_PER_SESSION: int = int(os.getenv("MAX_WORKFLOW_RUNS_PER_SESSION", "20"))

    ENRICHMENT_ENGINE: str = os.getenv("ENRICHMENT_ENGINE", "bs4")


settings = Settings()
