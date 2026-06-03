from collections.abc import Generator

from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from database.connection import engine

SessionLocal = (
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    if engine
    else None
)


def get_db_session() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Database is not configured. Set DATABASE_URL.",
        )

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()