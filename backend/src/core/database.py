from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import StaticPool
from .config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        poolclass=StaticPool,
        echo=settings.DEBUG,
    )
else:
    engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


# Columns added after initial schema — (table, column, DDL)
_MIGRATIONS = [
    ("users", "gender",             "VARCHAR"),
    ("users", "country",            "VARCHAR"),
    ("users", "bio",                "VARCHAR"),
    ("users", "avatar_url",         "VARCHAR"),
    ("users", "closet_visibility",  "VARCHAR NOT NULL DEFAULT 'private'"),
]


def _apply_migrations() -> None:
    """Add any missing columns to existing tables (safe to run every startup)."""
    with engine.connect() as conn:
        for table, column, col_def in _MIGRATIONS:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}"))
                conn.commit()
                logger.info(f"Migration applied: {table}.{column}")
            except OperationalError:
                pass  # Column already exists — no-op


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _apply_migrations()
    logger.info("Database tables ready")


def get_session():
    with Session(engine) as session:
        yield session
