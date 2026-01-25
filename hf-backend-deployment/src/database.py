from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool, StaticPool
from sqlmodel import Session
from .core.config import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create engine with production-ready settings
def create_db_engine():
    # Connection arguments vary based on database type
    connect_args = {}
    pool_class = None

    if "sqlite" in settings.DATABASE_URL:
        # SQLite-specific settings
        connect_args = {"check_same_thread": False}
        pool_class = StaticPool if settings.ENVIRONMENT == "development" else QueuePool
    else:
        # PostgreSQL/MySQL-specific settings
        connect_args = {
            "connect_timeout": 10,
            "command_timeout": 30,
        }
        pool_class = QueuePool

    # Engine configuration for production
    engine_kwargs = {
        "pool_pre_ping": True,  # Verify connections before use
        "pool_recycle": 300,    # Recycle connections every 5 minutes
        "pool_size": 20,        # Initial pool size
        "max_overflow": 30,     # Max overflow connections
        "pool_timeout": 30,     # Timeout for getting connection from pool
        "echo": settings.DEBUG, # Log SQL queries in development
    }

    if pool_class:
        engine_kwargs["poolclass"] = pool_class

    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        **engine_kwargs
    )

    logger.info(f"Database engine created for {settings.ENVIRONMENT} environment")
    return engine

engine = create_db_engine()

def get_session():
    with Session(engine) as session:
        yield session