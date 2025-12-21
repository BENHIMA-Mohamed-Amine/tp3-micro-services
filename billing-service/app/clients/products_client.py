import httpx
from app.consul_client import consul_client


class ProductsClient:
    """Client to communicate with the Inventory Service"""

    async def get_product(self, product_id: int):
        """Fetch product details by ID from Inventory Service"""
        # 1. Discover the service URL dynamically from Consul
        base_url = consul_client.get_service_url("inventory-service")
        if not base_url:
            raise Exception("❌ Inventory Service is unavailable (not found in Consul)")

        # 2. Make the Async HTTP Request
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{base_url}/products/{product_id}")

                if response.status_code == 404:
                    return None

                # Raise an exception for 500 errors or connection issues
                response.raise_for_status()
                return response.json()

            except httpx.RequestError as e:
                print(f"❌ Error connecting to Inventory Service: {e}")
                raise e

    async def decrease_stock(self, product_id: int, quantity: int):
        """
        Decrease product stock by the given quantity.
        Calls PATCH /products/{id}/stock?quantity_delta=-{quantity}
        """
        base_url = consul_client.get_service_url("inventory-service")
        if not base_url:
            raise Exception("❌ Inventory Service is unavailable")

        # We are selling items, so we subtract from the stock (negative delta)
        quantity_delta = -quantity

        async with httpx.AsyncClient() as client:
            try:
                # We assume the Inventory Service uses a query parameter for the delta
                # based on standard FastAPI default behavior for simple arguments
                response = await client.patch(
                    f"{base_url}/products/{product_id}/stock",
                    params={"quantity_delta": quantity_delta},
                )

                if response.status_code == 404:
                    raise Exception(
                        f"Product {product_id} not found during stock update"
                    )

                if response.status_code == 400:
                    # Likely insufficient stock
                    error_detail = response.json().get("detail", "Unknown error")
                    raise Exception(f"Stock update failed: {error_detail}")

                response.raise_for_status()
                return response.json()

            except httpx.RequestError as e:
                print(f"❌ Failed to update stock for product {product_id}: {e}")
                raise e


# Create a global instance
products_client = ProductsClient()
