"""SQLAlchemy declarative base configuration.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

from datetime import UTC, datetime

from sqlalchemy.orm import DeclarativeBase


def get_utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""

    pass
