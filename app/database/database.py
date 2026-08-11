from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import DATABASE_URL
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
    bind=engine
)

# Classe de base pour les modèles
Base = declarative_base()