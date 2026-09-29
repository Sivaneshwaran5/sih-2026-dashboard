"""
Bharat Urban Intelligence Platform (BEL - SIH 2026)
Database Integration Layer: SQLAlchemy & SQLite Configuration
Problem Statement: SIH26124

Configures SQLite database connection, sessionmaker, declarative base,
and FastAPI generator dependency for graceful per-request session lifecycle.
"""

import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

# 1. Automatic resolution of SQLite database in the project root directory
BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATABASE_PATH: str = os.path.join(BASE_DIR, "urban_intel.db")
SQLALCHEMY_DATABASE_URL: str = f"sqlite:///{DATABASE_PATH}"

# 2. Configure engine with check_same_thread=False for FastAPI async multi-threading
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

# 3. Thread-safe sessionmaker factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# 4. Declarative ORM base
class Base(DeclarativeBase):
    pass


# 5. Dependency for injecting DB sessions into FastAPI route handlers
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields an isolated SQLAlchemy database session
    per HTTP request and guarantees graceful closure in the finally block.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
