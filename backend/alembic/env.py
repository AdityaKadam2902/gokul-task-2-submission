"""Alembic Environment Configuration.

Gokul Infocare - AI Growth & Automation Associate - Task 2
Candidate Number: 267
Engineering Baseline: Blueprint v0.2
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure backend directory is in python search path
root_dir = Path(__file__).resolve().parent.parent.parent
backend_dir = root_dir / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.core.config import get_settings  # noqa: E402
from app.db.session import configure_sqlite_engine, init_db_dir  # noqa: E402
from app.models import Base  # noqa: E402

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata for autogenerate
target_metadata = Base.metadata

# Use configured database URL from application settings or caller override
settings = get_settings()
custom_url = config.get_main_option("sqlalchemy.url")
if custom_url and custom_url != "sqlite:///./backend/data/labinsight.db":
    # Caller explicitly configured a custom test URL (e.g. test_migrations)
    pass
elif settings.database_url:
    config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    """
    url = config.get_main_option("sqlalchemy.url") or settings.database_url
    init_db_dir(url)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """
    url = config.get_main_option("sqlalchemy.url") or settings.database_url
    init_db_dir(url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    if str(url).startswith("sqlite"):
        configure_sqlite_engine(connectable)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
