"""Database connection and session management for SQLite in-memory database"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from typing import Generator

from app.db.schema import Base
from app.logging_config import get_logger

logger = get_logger(__name__)

# SQLite in-memory database with connection pooling
DATABASE_URL = "sqlite:///./test.db"

# Create engine with StaticPool for in-memory SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database schema"""
    logger.info("initializing_database", database="sqlite_in_memory")
    Base.metadata.create_all(bind=engine)
    logger.info("database_initialized", tables=list(Base.metadata.tables.keys()))


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

