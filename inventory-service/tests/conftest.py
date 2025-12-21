import pytest
from sqlmodel import SQLModel, create_engine, Session

from app import database
from app import main as app_main
from app.main import app


@pytest.fixture
def engine():
    """Create a pure in-memory SQLite engine for tests using StaticPool."""
    from sqlalchemy.pool import StaticPool

    url = "sqlite:///:memory:"
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        pool_pre_ping=True,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create a fresh session for a test."""
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(monkeypatch, engine):
    """TestClient that overrides DB dependency and suppresses Consul registration."""

    # Override get_session dependency to use test engine
    def get_session_override():
        with Session(engine) as s:
            yield s

    # Override the module-level engine
    monkeypatch.setattr(database, "engine", engine)

    # Override the dependency used by routers
    monkeypatch.setitem(
        app.dependency_overrides, database.get_session, get_session_override
    )

    # Try to override specifically for the products router if imported there
    try:
        from app.routers import products as products_router

        monkeypatch.setitem(
            app.dependency_overrides, products_router.get_session, get_session_override
        )
    except Exception:
        pass

    # Prevent real startup (DB creation on prod DB, Consul registration)
    monkeypatch.setattr(app_main, "create_db_and_tables", lambda: None)

    # Suppress consul register/deregister
    try:
        monkeypatch.setattr(app_main.consul_client, "register_service", lambda: None)
        monkeypatch.setattr(app_main.consul_client, "deregister_service", lambda: None)
    except Exception:
        pass

    # Ensure metadata is created on the test engine
    SQLModel.metadata.create_all(engine)

    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
