from sqlmodel import create_engine, Session, SQLModel
from .config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=True if settings.environment == "development" else False,  # Log SQL queries in dev
    pool_pre_ping=True,  # Verify connections before using them
)


def create_db_and_tables():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency function to get database session"""
    with Session(engine) as session:
        yield session