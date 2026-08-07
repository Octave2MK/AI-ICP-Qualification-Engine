from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import DATABASE_URL

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# Fabrique de sessions
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

# Classe de base pour les modèles
Base = declarative_base()