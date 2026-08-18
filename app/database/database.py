from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import DATABASE_URL
import os
DEBUG_SQL = os.getenv("SQL_DEBUG", "false").lower() == "true"

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=DEBUG_SQL
)

# Fabrique de sessions
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    bind=engine
)

# Classe de base pour les modèles
Base = declarative_base()


def init_db() -> None:
    """Crée les tables manquantes et applique les migrations additives.

    Point d'entrée unique pour le bootstrap du schéma, afin que les
    couches appelantes (ex. l'UI) n'aient pas à connaître les détails de
    SQLAlchemy/du schéma."""
    import app.database.models  # noqa: F401  (enregistre les modèles sur Base.metadata)
    from app.database.schema import ensure_schema

    Base.metadata.create_all(bind=engine)
    ensure_schema()