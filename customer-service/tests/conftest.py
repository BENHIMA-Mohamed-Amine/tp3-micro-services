import pytest
from sqlmodel import SQLModel, create_engine, Session

from app import database
from app import main as app_main
from app.main import app


@pytest.fixture
def engine():
    """Create a pure in-memory SQLite engine for tests using StaticPool.

    Using StaticPool with :memory: keeps the same connection open and shared
    across threads, so the TestClient and sessions see the same DB without
    writing any temporary file to disk.
    """
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

    # Also replace the module-level engine used by the app so any code that
    # references `app.database.engine` will use the test engine
    monkeypatch.setattr(database, "engine", engine)

    # Override the DI used by routers: ensure the app uses the test session
    # The dependency function object used by routes is `database.get_session`
    monkeypatch.setitem(
        app.dependency_overrides, database.get_session, get_session_override
    )

    # Also ensure we override the specific dependency object imported in the router module
    try:
        from app.routers import customers as customers_router

        monkeypatch.setitem(
            app.dependency_overrides, customers_router.get_session, get_session_override
        )
    except Exception:
        pass

    # Prevent the real startup from registering with Consul and creating prod tables
    # Make startup a no-op (we'll create tables explicitly on the test engine)
    monkeypatch.setattr(app_main, "create_db_and_tables", lambda: None)

    # Ensure the module-level engine is our test engine and create tables on it
    monkeypatch.setattr(database, "engine", engine)
    SQLModel.metadata.create_all(engine)

    # Suppress consul register/deregister on the instance used by main
    try:
        monkeypatch.setattr(app_main.consul_client, "register_service", lambda: None)
        monkeypatch.setattr(app_main.consul_client, "deregister_service", lambda: None)
    except Exception:
        pass

    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
