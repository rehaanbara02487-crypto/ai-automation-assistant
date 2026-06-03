import logging

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings

logger = logging.getLogger("beingai.database")


class Base(DeclarativeBase):
    metadata = MetaData(schema="public")


def get_database_url() -> str:
    return get_settings().database_url.strip()


def create_database_engine() -> Engine | None:
    database_url = get_database_url()
    if not database_url:
        logger.warning("DATABASE_URL is not set. PostgreSQL persistence is disabled.")
        return None

    return create_engine(
        database_url,
        pool_pre_ping=True,
        future=True,
    )


engine = create_database_engine()


def create_database_tables() -> None:
    if engine is None:
        logger.warning("Skipping database table creation because DATABASE_URL is missing.")
        return

    from database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
