from unittest.mock import MagicMock
from app.consul_client import consul_client
from app.config import settings


def test_settings_loaded_from_env():
    # Basic assertions about loaded settings
    assert settings.service_name == "inventory-service"
    assert isinstance(settings.service_port, int)


def test_consul_register_calls_agent(monkeypatch):
    # Mock the internal consul object
    fake_consul = MagicMock()
    fake_consul.agent = MagicMock()
    fake_consul.agent.service = MagicMock()

    monkeypatch.setattr(consul_client, "consul", fake_consul)

    # Call methods
    consul_client.register_service()
    consul_client.deregister_service()

    # Assert calls were made
    assert fake_consul.agent.service.register.called
    assert fake_consul.agent.service.deregister.called
