import consul
from .config import settings


class ConsulClient:
    """Client for Consul service registration"""

    def __init__(self):
        self.consul = consul.Consul(
            host=settings.consul_host, port=settings.consul_port
        )
        self.service_id = f"{settings.service_name}-{settings.service_port}"

    def register_service(self):
        """Register this service with Consul"""
        try:
            self.consul.agent.service.register(
                name=settings.service_name,
                service_id=self.service_id,
                address=settings.service_host,
                port=settings.service_port,
                tags=[
                    "fastapi",
                    "microservice",
                    "traefik.enable=true",
                    f"traefik.http.routers.{settings.service_name}.rule=PathPrefix(`/api/products`)",
                    f"traefik.http.services.{settings.service_name}.loadbalancer.server.port={settings.service_port}",
                ],
                check=consul.Check.http(
                    url=f"http://{settings.service_host}:{settings.service_port}/health",
                    interval="10s",
                    timeout="5s",
                    deregister="30s",
                ),
            )
            print(f"✅ Service {self.service_id} registered with Consul")
        except Exception as e:
            print(f"❌ Failed to register service with Consul: {e}")

    def deregister_service(self):
        """Deregister this service from Consul"""
        try:
            self.consul.agent.service.deregister(self.service_id)
            print(f"✅ Service {self.service_id} deregistered from Consul")
        except Exception as e:
            print(f"❌ Failed to deregister service: {e}")


# Create a global instance
consul_client = ConsulClient()
