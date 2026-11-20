"""Pytest fixtures for isolated database testing.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from app.db.session import create_db_engine, get_db
from app.main import app
from app.models.base import Base
from fastapi.testclient import TestClient
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="function")
def isolated_db_url() -> Generator[str, None, None]:
    """Provide a temporary SQLite database URL isolated per test function."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = Path(tmp_dir) / "test_isolated.db"
        yield f"sqlite:///{db_path}"


@pytest.fixture(scope="function")
def test_engine(isolated_db_url: str) -> Generator[Engine, None, None]:
    """Create a configured test engine with tables created from metadata."""
    engine = create_db_engine(isolated_db_url)
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_engine: Engine) -> Generator[Session, None, None]:
    """Provide an isolated database session with rollback on completion."""
    session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine, class_=Session
    )
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def api_client(test_db_session: Session) -> Generator[TestClient, None, None]:
    """Provide a FastAPI TestClient bound to the isolated test database session."""

    def override_get_db() -> Generator[Session, None, None]:
        yield test_db_session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    try:
        yield client
    finally:
        app.dependency_overrides.clear()
