import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel import SQLModel, create_engine, Session

from app import database
from app import main as app_main
from app.main import app

# Import the global client instances to mock them
from app.services import billing_service as service_module


@pytest.fixture
def engine():
    """Create a pure in-memory SQLite engine for tests."""
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
def mock_external_clients(monkeypatch):
    """
    Mock the external customer and product clients.
    This fixture is automatically used by the client fixture,
    but can also be used explicitly in service tests.
    """
    # 1. Mock CustomerClient
    mock_cust_client = AsyncMock()
    # Default behavior: Return a valid customer
    mock_cust_client.get_customer.return_value = {
        "id": 1,
        "name": "Test Customer",
        "email": "test@test.com",
    }
    monkeypatch.setattr(service_module, "customer_client", mock_cust_client)

    # 2. Mock ProductsClient
    mock_prod_client = AsyncMock()
    # Default behavior: Return a valid product with price 10.0
    mock_prod_client.get_product.return_value = {
        "id": 1,
        "name": "Test Product",
        "price": 10.0,
        "quantity": 100,
    }
    mock_prod_client.decrease_stock.return_value = True
    monkeypatch.setattr(service_module, "products_client", mock_prod_client)

    return mock_cust_client, mock_prod_client


@pytest.fixture
def client(monkeypatch, engine, mock_external_clients):
    """TestClient that overrides DB and Mocks External Services."""

    # Override get_session dependency
    def get_session_override():
        with Session(engine) as s:
            yield s

    monkeypatch.setattr(database, "engine", engine)

    # Override dependency in main app and specific router
    monkeypatch.setitem(
        app.dependency_overrides, database.get_session, get_session_override
    )

    try:
        from app.routers import bills as bills_router

        monkeypatch.setitem(
            app.dependency_overrides, bills_router.get_session, get_session_override
        )
    except Exception:
        pass

    # Disable Consul Registration during tests
    monkeypatch.setattr(app_main, "create_db_and_tables", lambda: None)
    try:
        monkeypatch.setattr(app_main.consul_client, "register_service", lambda: None)
        monkeypatch.setattr(app_main.consul_client, "deregister_service", lambda: None)
    except Exception:
        pass

    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c
