"""Database configuration and session management."""

from typing import Generator
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.core.config import Settings


Base = declarative_base()


def init_database(settings: Settings) -> Engine:
    """Initialize database engine with SQLite configuration."""

    # Import models to register them with Base
    from app.models import Project, Chapter  # noqa: F401

    # SQLite specific configuration
    connect_args = {
        "check_same_thread": False,  # Required for SQLite with FastAPI
    }

    # Create engine
    engine = create_engine(
        settings.database_url,
        connect_args=connect_args,
        poolclass=StaticPool,  # Use StaticPool for SQLite
        echo=settings.debug,
    )

    # Enable foreign keys for SQLite
    if "sqlite" in settings.database_url:

        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # Create all tables
    Base.metadata.create_all(bind=engine)

    return engine


def get_db(engine: Engine) -> Generator[Session, None, None]:
    """Get database session generator."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Global SessionLocal will be initialized after engine creation
SessionLocal = None


def init_session_factory(engine: Engine) -> None:
    """Initialize the global session factory."""
    global SessionLocal
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """Get database session for FastAPI dependency injection."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_session_factory first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
