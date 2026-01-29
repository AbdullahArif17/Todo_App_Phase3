from sqlmodel import create_engine, Session
from src.core.config import settings
from sqlalchemy.pool import QueuePool
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create the database engine
def create_db_engine():
    """
    Create a database engine with production-ready settings
    """
    connect_args = {}

    if "sqlite" in settings.DATABASE_URL.lower():
        # SQLite-specific settings
        connect_args = {"check_same_thread": False}
    else:
        # PostgreSQL-specific settings
        connect_args = {
            "connect_timeout": 10,
        }

    # Engine configuration for production
    engine_kwargs = {
        "pool_pre_ping": True,  # Verify connections before use
        "pool_recycle": 300,    # Recycle connections every 5 minutes
        "pool_size": 20,        # Initial pool size
        "max_overflow": 30,     # Max overflow connections
        "pool_timeout": 30,     # Timeout for getting connection from pool
        "echo": settings.DEBUG, # Log SQL queries in development
        "poolclass": QueuePool,
    }

    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        **engine_kwargs
    )

    logger.info(f"Database engine created for {settings.ENVIRONMENT} environment")
    return engine

# Create the global engine instance
engine = create_db_engine()

from contextlib import contextmanager
from typing import Generator

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Context manager that provides a database session
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()