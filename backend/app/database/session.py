import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from backend.app.config import settings
from backend.app.database.models import Base

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

# Async session factory
AsyncSessionFactory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for obtaining async DB session in API endpoints."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables and seed initial registries."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Migrate any missing columns in simulations table for SQLite compatibility
        await conn.run_sync(_migrate_simulations_table)


def _migrate_simulations_table(sync_conn):
    """Refreshes sqlite schema if new columns were added to Simulation model."""
    try:
        from sqlalchemy import text
        res = sync_conn.execute(text("PRAGMA table_info(simulations)"))
        existing_cols = {row[1] for row in res.fetchall()}
    except Exception:
        return

    cols_to_add = {
        "remote_status": "VARCHAR(50)",
        "diagnostic_code": "VARCHAR(50) DEFAULT 'NONE'",
        "root_cause_type": "VARCHAR(100)",
        "root_cause_confidence": "VARCHAR(20) DEFAULT 'UNKNOWN'",
        "position_count": "INTEGER",
        "diagnostic_details": "JSON",
        "retry_count": "INTEGER DEFAULT 0",
        "diagnostic_reason": "TEXT",
        "possible_cause": "TEXT",
        "raw_response": "JSON",
        "portfolio_status": "VARCHAR(50) DEFAULT 'UNKNOWN'",
        "metrics_status": "VARCHAR(50) DEFAULT 'UNKNOWN'",
        "classification": "VARCHAR(50) DEFAULT 'PENDING'"
    }

    from sqlalchemy import text
    for col_name, col_type in cols_to_add.items():
        if col_name not in existing_cols:
            try:
                sync_conn.execute(text(f"ALTER TABLE simulations ADD COLUMN {col_name} {col_type}"))
            except Exception:
                pass

