"""
Test configuration and fixtures.
"""

import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.core.database import Base, init_session_factory
from app.core.config import settings


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a test database session."""
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Import models to register them
    from app.models.project import Project  # noqa
    from app.models.chapter import Chapter  # noqa
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize session factory for dependency injection
    init_session_factory(engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)