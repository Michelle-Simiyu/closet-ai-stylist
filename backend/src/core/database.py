from sqlmodel import SQLModel, create_engine, Session
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


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created")


def get_session():
    with Session(engine) as session:
        yield session
