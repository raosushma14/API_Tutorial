from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

class Base(DeclarativeBase):
    pass

# Sync SQLAlchemy engine (simple to learn)
engine = create_engine(settings.database_url, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Dependency for FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
