from unittest.mock import MagicMock
from app.consul_client import consul_client
from app.config import settings


def test_settings_loaded():
    assert settings.service_name == "billing-service"
    assert isinstance(settings.service_port, int)


def test_consul_register_calls_agent(monkeypatch):
    # Mock the internal consul object
    fake_consul = MagicMock()
    fake_consul.agent = MagicMock()
    fake_consul.agent.service = MagicMock()

    monkeypatch.setattr(consul_client, "consul", fake_consul)

    consul_client.register_service()
    fake_consul.agent.service.register.assert_called()

    consul_client.deregister_service()
    fake_consul.agent.service.deregister.assert_called()
