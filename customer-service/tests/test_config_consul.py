from unittest.mock import Mock

import app.config as config_module
import app.consul_client as consul_module


def test_settings_loads_and_consul_register(monkeypatch):
    # load settings and ensure fields exist
    s = config_module.Settings()
    assert hasattr(s, "service_name")

    # mock consul client to verify register called
    # make a fake Consul object and ensure Consul.Consul() returns it
    mock_consul = Mock()
    fake_module = Mock()
    fake_module.Consul.return_value = mock_consul
    monkeypatch.setattr(consul_module, "consul", fake_module)

    # call register and deregister using the client API (no extra args)
    client = consul_module.ConsulClient()
    client.register_service()
    client.deregister_service()

    assert mock_consul.agent.service.register.called
    assert mock_consul.agent.service.deregister.called


from unittest.mock import MagicMock

from app.consul_client import consul_client
from app.config import settings


def test_settings_loaded_from_env():
    # Basic assertions about loaded settings
    assert settings.service_name == "customer-service"
    assert isinstance(settings.service_port, int)


def test_consul_register_calls_agent(monkeypatch):
    # Replace the entire consul client with a mock that exposes agent.service.register/deregister
    fake_consul = MagicMock()
    fake_consul.agent = MagicMock()
    fake_consul.agent.service = MagicMock()
    mock_register = fake_consul.agent.service.register
    mock_deregister = fake_consul.agent.service.deregister

    monkeypatch.setattr(consul_client, "consul", fake_consul)

    consul_client.register_service()
    mock_register.assert_called()

    consul_client.deregister_service()
    mock_deregister.assert_called()
