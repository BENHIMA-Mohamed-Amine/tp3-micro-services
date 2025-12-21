import consul
import random
from app.config import settings


class ConsulClient:
    """Client for Consul service registration and discovery"""

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
                    # Note: We updated the rule to /api/bills for this service
                    f"traefik.http.routers.{settings.service_name}.rule=PathPrefix(`/api/bills`)",
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

    def get_service_url(self, service_name: str) -> str:
        """
        Discover a healthy service instance from Consul.
        Returns the base URL (e.g., 'http://172.18.0.4:8081')
        """
        try:
            # catalog.service returns a tuple: (index, nodes)
            _, nodes = self.consul.catalog.service(service_name)

            if not nodes:
                print(f"⚠️ No instances found for service: {service_name}")
                return None

            # Simple Load Balancing: Choose a random instance
            service = random.choice(nodes)

            # Prefer ServiceAddress, fall back to node Address if ServiceAddress is empty
            address = service.get("ServiceAddress") or service.get("Address")
            port = service.get("ServicePort")

            return f"http://{address}:{port}"

        except Exception as e:
            print(f"❌ Failed to discover service {service_name}: {e}")
            return None


# Create a global instance
consul_client = ConsulClient()
