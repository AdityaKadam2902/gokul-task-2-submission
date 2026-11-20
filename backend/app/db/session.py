"""Database Engine and Session Management Infrastructure.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import logging
import sqlite3
from collections.abc import Generator
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger("labinsight.db")


def init_db_dir(database_url: str) -> None:
    """Ensure the directory for SQLite database file exists before connecting."""
    if database_url.startswith("sqlite:///"):
        # Strip sqlite:/// prefix
        db_path_str = database_url.replace("sqlite:///", "")
        # Handle in-memory database
        if db_path_str == ":memory:":
            return
        db_path = Path(db_path_str).resolve()
        parent_dir = db_path.parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Created database directory: %s", parent_dir)


def configure_sqlite_engine(target_engine: Engine) -> None:
    """Attach connection listeners for SQLite PRAGMAs.

    - Enforces foreign key constraints (PRAGMA foreign_keys=ON)
    - Sets Write-Ahead Logging for concurrency (PRAGMA journal_mode=WAL)
    - Sets busy timeout to prevent locking conflicts (PRAGMA busy_timeout=5000)
    """

    @event.listens_for(target_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        if isinstance(dbapi_connection, sqlite3.Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()


def create_db_engine(database_url: str) -> Engine:
    """Factory creating and configuring an isolated SQLAlchemy Engine."""
    init_db_dir(database_url)

    connect_args: dict[str, Any] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        connect_args["timeout"] = 5.0

    eng = create_engine(
        database_url,
        connect_args=connect_args,
        echo=False,
        future=True,
    )

    if database_url.startswith("sqlite"):
        configure_sqlite_engine(eng)

    return eng


# Application Default Engine & Session Factory
settings = get_settings()
engine = create_db_engine(settings.database_url)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """Dependency injection provider yielding a scoped database session.

    Ensures the session is cleanly closed upon completion of the request.
    Transactions must remain short; never keep sessions open across external I/O.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connectivity() -> tuple[bool, str | None]:
    """Execute a lightweight connectivity probe against the active database engine.

    Returns:
        (True, None) if the connection succeeds.
        (False, error_message) if the connection fails or tables are inaccessible.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        logger.warning("Database connectivity check failed: %s", exc)
        return False, str(exc)
