from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()

# URL de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///data/icp.db"
)

@dataclass(frozen=True)
class Settings:
    """Configuration globale de l'application."""

    REQUEST_TIMEOUT: int = 10

    SEARCH_PROVIDER: str = os.getenv(
    "SEARCH_PROVIDER",
    "searxng",
    )

    SEARXNG_BASE_URL: str = os.getenv(
        "SEARXNG_BASE_URL",
        "http://localhost:8080",
    )

    SEARXNG_TIMEOUT: int = int(
        os.getenv(
            "SEARXNG_TIMEOUT",
            "30",
        )
    )

    SEARCH_RETRY_ATTEMPTS: int = int(
        os.getenv(
            "SEARCH_RETRY_ATTEMPTS",
            "3",
        )
    )

    SEARCH_RETRY_DELAY: float = float(
        os.getenv(
            "SEARCH_RETRY_DELAY",
            "1",
        )
    )

    SEARCH_RATE_LIMIT_INTERVAL: float = float(
        os.getenv(
            "SEARCH_RATE_LIMIT_INTERVAL",
            "1",
        )
    )
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0 Safari/537.36"
    )

    LLM_PROVIDER: str = os.getenv(
        "LLM_PROVIDER",
        "gemini",
    )

    GEMINI_API_KEY: str = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    GEMINI_MODEL: str = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash",
    )

    OPENAI_API_KEY: str = os.getenv(
        "OPENAI_API_KEY",
        "",
    )

settings = Settings()