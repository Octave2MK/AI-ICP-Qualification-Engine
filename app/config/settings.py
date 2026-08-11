from dataclasses import dataclass
from dotenv import load_dotenv
import os

# Charger les variables du fichier .env
load_dotenv()

# URL de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///data/icp.db"
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

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""
)
