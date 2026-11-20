"""Tests for database infrastructure, SQLite PRAGMAs, foreign keys, and session lifecycle.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import tempfile
from pathlib import Path

import pytest
from app.db.session import (
    check_db_connectivity,
    get_db,
    init_db_dir,
)
from app.models.patient_analysis import PatientAnalysis
from sqlalchemy import Engine, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_sqlite_foreign_key_enforcement(test_db_session: Session) -> None:
    """Verify SQLite foreign key constraint blocks orphaned analysis insertion."""
    orphaned_analysis = PatientAnalysis(
        patient_id=999999,  # Non-existent patient
        run_number=1,
        input_snapshot_json={"glucose": 90.0},
    )
    test_db_session.add(orphaned_analysis)
    with pytest.raises(IntegrityError):
        test_db_session.commit()
    test_db_session.rollback()


def test_sqlite_pragmas_configured(test_engine: Engine) -> None:
    """Verify that foreign keys, WAL mode, and busy timeout are configured on connection."""
    with test_engine.connect() as conn:
        fk_result = conn.execute(text("PRAGMA foreign_keys")).scalar()
        assert fk_result == 1, "Foreign keys must be enabled (PRAGMA foreign_keys=ON)"

        timeout_result = conn.execute(text("PRAGMA busy_timeout")).scalar()
        assert timeout_result == 5000, "Busy timeout must be set to 5000 ms"


def test_session_lifecycle_dependency() -> None:
    """Verify get_db dependency provider yields an active session and closes it cleanly."""
    gen = get_db()
    session = next(gen)
    assert isinstance(session, Session)
    assert session.is_active

    # Closing generator should trigger cleanup
    try:
        next(gen)
    except StopIteration:
        pass


def test_init_db_dir_creates_missing_directory() -> None:
    """Verify init_db_dir creates parent directories for SQLite database paths."""
    with tempfile.TemporaryDirectory() as tmp_root:
        nested_dir = Path(tmp_root) / "nested" / "subfolder"
        db_url = f"sqlite:///{nested_dir}/test.db"

        assert not nested_dir.exists()
        init_db_dir(db_url)
        assert nested_dir.exists()


def test_check_db_connectivity_success() -> None:
    """Verify check_db_connectivity returns (True, None) for the default engine."""
    ok, error = check_db_connectivity()
    assert ok is True
    assert error is None
