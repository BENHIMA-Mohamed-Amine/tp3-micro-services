import httpx
from app.consul_client import consul_client


class CustomerClient:
    async def get_customer(self, customer_id: int):
        base_url = consul_client.get_service_url("customer-service")
        if not base_url:
            raise Exception("Customer service unavailable")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{base_url}/customers/{customer_id}")
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Error fetching customer: {e}")
                raise e


# Create global instance
customer_client = CustomerClient()
