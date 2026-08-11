"""Alembic environment — supports both offline (SQL dump) and online (live DB) modes.

Works with SQLite (local dev) and PostgreSQL (production/Docker).
The pgvector extension is enabled automatically when running against PostgreSQL.
"""
from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, text
from alembic import context

# ── Load app settings and models ─────────────────────────────────────────────
# Import settings so DATABASE_URL is read from the .env file
from app.core.config import settings

# Import Base and every model so Alembic can see the full schema.
from app.core.database import Base
import app.models  # noqa: F401 — registers User, Resume, InterviewSession, etc.

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url with the value from our settings so we never
# hard-code credentials in alembic.ini.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Logging setup from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata Alembic will compare against the live schema
target_metadata = Base.metadata


def _enable_pgvector(connection) -> None:
    """Create the vector extension when running against PostgreSQL."""
    if connection.dialect.name == "postgresql":
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


# ── Offline mode (generate SQL without connecting) ───────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Render the correct SQL for enum types in PostgreSQL
        render_as_batch=url.startswith("sqlite"),
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (connect to the real database) ────────────────────────────────
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        _enable_pgvector(connection)
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite does not support ALTER TABLE — use batch mode for SQLite only
            render_as_batch=settings.is_sqlite,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
