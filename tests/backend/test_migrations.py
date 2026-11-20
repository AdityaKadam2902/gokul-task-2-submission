"""Tests for Alembic migrations on isolated databases.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import tempfile
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, pool


def test_alembic_migration_lifecycle_fresh_database() -> None:
    """Verify that Alembic migrations apply cleanly to a brand new isolated database and can downgrade."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_db_path = Path(tmp_dir) / "fresh_migration_test.db"
        test_db_url = f"sqlite:///{test_db_path}"

        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

        # 1. Upgrade to head
        command.upgrade(alembic_cfg, "head")

        # 2. Inspect created tables
        engine = create_engine(test_db_url, poolclass=pool.NullPool)
        try:
            inspector = inspect(engine)
            table_names = inspector.get_table_names()
            assert "patients" in table_names
            assert "patient_analyses" in table_names
            assert "alembic_version" in table_names

            # 3. Check columns in patients
            patient_cols = [col["name"] for col in inspector.get_columns("patients")]
            assert "id" in patient_cols
            assert "full_name" in patient_cols
            assert "date_of_birth" in patient_cols
            assert "email" in patient_cols
            assert "glucose_value" in patient_cols
            assert "haemoglobin_value" in patient_cols
            assert "cholesterol_value" in patient_cols
            assert "unit_profile_code" in patient_cols

            # 4. Check columns in patient_analyses
            analyses_cols = [col["name"] for col in inspector.get_columns("patient_analyses")]
            assert "id" in analyses_cols
            assert "patient_id" in analyses_cols
            assert "run_number" in analyses_cols
            assert "input_snapshot_json" in analyses_cols
            assert "overall_status" in analyses_cols

            # 5. Downgrade to base
            command.downgrade(alembic_cfg, "base")
            inspector_post_downgrade = inspect(engine)
            post_tables = inspector_post_downgrade.get_table_names()
            assert "patients" not in post_tables
            assert "patient_analyses" not in post_tables

            # 6. Re-upgrade to head
            command.upgrade(alembic_cfg, "head")
            inspector_reup = inspect(engine)
            assert "patients" in inspector_reup.get_table_names()
        finally:
            engine.dispose()
