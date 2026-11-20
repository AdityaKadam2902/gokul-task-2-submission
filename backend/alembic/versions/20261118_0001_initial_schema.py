"""Initial schema for patients and patient_analyses.

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-11-18 01:25:00.000000

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Create 'patients' table
    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("glucose_value", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("haemoglobin_value", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("cholesterol_value", sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column("unit_profile_code", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_patients_email"), "patients", ["email"], unique=False)

    # 2. Create 'patient_analyses' table
    op.create_table(
        "patient_analyses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("run_number", sa.Integer(), nullable=False),
        sa.Column("input_snapshot_json", sa.JSON(), nullable=False),
        sa.Column("external_provider", sa.String(length=60), nullable=False),
        sa.Column("external_api_version", sa.String(length=40), nullable=True),
        sa.Column("external_status", sa.String(length=20), nullable=False),
        sa.Column("external_result_json", sa.JSON(), nullable=True),
        sa.Column("ai_provider", sa.String(length=40), nullable=True),
        sa.Column("ai_model", sa.String(length=80), nullable=True),
        sa.Column("ai_status", sa.String(length=20), nullable=False),
        sa.Column("ai_result_json", sa.JSON(), nullable=True),
        sa.Column("remarks_text", sa.Text(), nullable=True),
        sa.Column("overall_status", sa.String(length=20), nullable=False),
        sa.Column("ruleset_version", sa.String(length=40), nullable=True),
        sa.Column("prompt_version", sa.String(length=40), nullable=True),
        sa.Column("error_code", sa.String(length=80), nullable=True),
        sa.Column("error_summary", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_of_id", sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="fk_patient_analyses_patient_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["retry_of_id"],
            ["patient_analyses.id"],
            name="fk_patient_analyses_retry_of_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("patient_id", "run_number", name="uq_patient_analyses_patient_run"),
    )
    op.create_index(
        op.f("ix_patient_analyses_patient_id"),
        "patient_analyses",
        ["patient_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_patient_analyses_overall_status"),
        "patient_analyses",
        ["overall_status"],
        unique=False,
    )
    op.create_index(
        "ix_patient_analyses_patient_created",
        "patient_analyses",
        ["patient_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_patient_analyses_status_created",
        "patient_analyses",
        ["overall_status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_patient_analyses_status_created", table_name="patient_analyses")
    op.drop_index("ix_patient_analyses_patient_created", table_name="patient_analyses")
    op.drop_index(op.f("ix_patient_analyses_overall_status"), table_name="patient_analyses")
    op.drop_index(op.f("ix_patient_analyses_patient_id"), table_name="patient_analyses")
    op.drop_table("patient_analyses")
    op.drop_index(op.f("ix_patients_email"), table_name="patients")
    op.drop_table("patients")
