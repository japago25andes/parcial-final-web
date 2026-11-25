"""Conexión a la base de datos PostgreSQL."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# La URL viene del docker-compose.yml. El valor por defecto sirve para correr sin Docker.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://biblioteca:biblioteca123@localhost:5432/biblioteca",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """Entrega una sesión de base de datos por cada petición y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
