"""Patient domain entity model.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, get_utc_now

if TYPE_CHECKING:
    from app.models.patient_analysis import PatientAnalysis


class Patient(Base):
    """Patient entity storing current contact details and blood biomarker measurements.

    Email is deliberately NOT globally unique, because the employer specification
    explicitly requires permitting duplicate patient record entry following user confirmation.
    """

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, index=True)
    glucose_value: Mapped[Decimal] = mapped_column(Numeric(10, 3, asdecimal=True), nullable=False)
    haemoglobin_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 3, asdecimal=True), nullable=False
    )
    cholesterol_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 3, asdecimal=True), nullable=False
    )
    unit_profile_code: Mapped[str] = mapped_column(
        String(40), nullable=False, default="ASSESSMENT_CONVENTIONAL_V1"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=get_utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=get_utc_now,
        onupdate=get_utc_now,
    )

    # Relationships: Deleting a patient cascades to all associated analysis runs
    analyses: Mapped[list["PatientAnalysis"]] = relationship(
        "PatientAnalysis",
        back_populates="patient",
        cascade="all, delete-orphan",
        order_by="PatientAnalysis.run_number",
    )
