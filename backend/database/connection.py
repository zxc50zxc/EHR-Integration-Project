from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.config import settings
from backend.database.models import Base


def _connect_args(database_url: str) -> dict[str, bool]:
    if "sqlite" in database_url:
        return {"check_same_thread": False}
    return {}


engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args(settings.DATABASE_URL),
    pool_pre_ping=True,
    echo=settings.DEBUG,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
