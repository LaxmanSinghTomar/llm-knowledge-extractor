"""Database models and connection management."""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Generator

Base = declarative_base()


class Analysis(Base):
    """Analysis model for storing text analysis results."""
    
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    title = Column(String(255), nullable=True)
    topics = Column(Text, nullable=False)  # JSON array as string
    sentiment = Column(String(20), nullable=False)
    keywords = Column(Text, nullable=False)  # JSON array as string
    confidence = Column(Text, nullable=False, default="0.0")  # Stored as string for simplicity
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, title={self.title})>"


def get_engine(database_url: str = "sqlite:///./knowledge_extractor.db"):
    """Create and return database engine."""
    return create_engine(
        database_url,
        connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )


def init_db(database_url: str = "sqlite:///./knowledge_extractor.db") -> None:
    """Initialize database tables."""
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)


def get_db(database_url: str = "sqlite:///./knowledge_extractor.db") -> Generator:
    """
    Database session dependency for FastAPI.
    
    Yields:
        Session: SQLAlchemy database session
    """
    engine = get_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

