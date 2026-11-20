"""PatientAnalysis domain entity model.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, get_utc_now
from app.models.enums import AiStatus, ExternalStatus, OverallStatus

if TYPE_CHECKING:
    from app.models.patient import Patient


def generate_uuid() -> str:
    """Generate string UUID primary key."""
    return str(uuid.uuid4())


class PatientAnalysis(Base):
    """Immutable analysis-run record preserving provider observation and AI remark provenance.

    Every analysis attempt is append-only; prior analysis runs are retained for auditability.
    """

    __tablename__ = "patient_analyses"
    __table_args__ = (
        UniqueConstraint("patient_id", "run_number", name="uq_patient_analyses_patient_run"),
        Index("ix_patient_analyses_patient_created", "patient_id", "created_at"),
        Index("ix_patient_analyses_status_created", "overall_status", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    patient_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Input snapshot contains strictly anonymous biomarker values & units; NO PII (name, email, DOB)
    input_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    # External Provider (TestWell) Provenance
    external_provider: Mapped[str] = mapped_column(String(60), nullable=False, default="testwell")
    external_api_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    external_status: Mapped[ExternalStatus] = mapped_column(
        SQLEnum(ExternalStatus, native_enum=False, length=20),
        nullable=False,
        default=ExternalStatus.PENDING,
    )
    external_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Local AI (Ollama llama3.2:3b) Provenance
    ai_provider: Mapped[str | None] = mapped_column(String(40), nullable=True, default="ollama")
    ai_model: Mapped[str | None] = mapped_column(String(80), nullable=True, default="llama3.2:3b")
    ai_status: Mapped[AiStatus] = mapped_column(
        SQLEnum(AiStatus, native_enum=False, length=20),
        nullable=False,
        default=AiStatus.PENDING,
    )
    ai_result_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    remarks_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Overall Lifecycle Status
    overall_status: Mapped[OverallStatus] = mapped_column(
        SQLEnum(OverallStatus, native_enum=False, length=20),
        nullable=False,
        default=OverallStatus.PENDING,
        index=True,
    )
    ruleset_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(40), nullable=True)

    # Bounded safe error metadata
    error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    error_summary: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=get_utc_now
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Historical lineage pointer for retries
    retry_of_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("patient_analyses.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="analyses")
