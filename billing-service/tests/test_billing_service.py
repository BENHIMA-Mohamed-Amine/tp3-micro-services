import pytest
from fastapi import HTTPException
from app.services.billing_service import BillingService
from app.models import BillCreate, BillItemCreate


@pytest.mark.asyncio
async def test_create_bill_success(session, mock_external_clients):
    mock_cust, mock_prod = mock_external_clients

    # Setup Data
    bill_data = BillCreate(
        customer_id=1, items=[BillItemCreate(product_id=100, quantity=2)]
    )

    # Initialize Service
    service = BillingService(session)

    # Execute
    bill = await service.create_bill(bill_data)

    # Assertions
    assert bill.customer_id == 1
    assert len(bill.items) == 1
    # Price was mocked as 10.0, quantity is 2, so subtotal = 20.0
    assert bill.total_amount == 20.0
    assert bill.items[0].sub_total == 20.0

    # Verify external calls
    mock_cust.get_customer.assert_called_with(1)
    mock_prod.get_product.assert_called_with(100)
    mock_prod.decrease_stock.assert_called_with(100, 2)


@pytest.mark.asyncio
async def test_create_bill_customer_not_found(session, mock_external_clients):
    mock_cust, _ = mock_external_clients
    # Simulate Customer 404
    mock_cust.get_customer.return_value = None

    service = BillingService(session)
    bill_data = BillCreate(customer_id=99, items=[])

    with pytest.raises(HTTPException) as exc:
        await service.create_bill(bill_data)

    assert exc.value.status_code == 404
    assert "Customer" in exc.value.detail


@pytest.mark.asyncio
async def test_create_bill_product_not_found(session, mock_external_clients):
    _, mock_prod = mock_external_clients
    # Simulate Product 404
    mock_prod.get_product.return_value = None

    service = BillingService(session)
    bill_data = BillCreate(
        customer_id=1, items=[BillItemCreate(product_id=999, quantity=1)]
    )

    with pytest.raises(HTTPException) as exc:
        await service.create_bill(bill_data)

    assert exc.value.status_code == 404
    assert "Product" in exc.value.detail


@pytest.mark.asyncio
async def test_create_bill_stock_error(session, mock_external_clients):
    _, mock_prod = mock_external_clients
    # Simulate Stock Update Failure (e.g. insufficient stock)
    mock_prod.decrease_stock.side_effect = Exception("Insufficient stock")

    service = BillingService(session)
    bill_data = BillCreate(
        customer_id=1, items=[BillItemCreate(product_id=100, quantity=5)]
    )

    with pytest.raises(HTTPException) as exc:
        await service.create_bill(bill_data)

    assert exc.value.status_code == 400
    assert "Insufficient stock" in exc.value.detail
