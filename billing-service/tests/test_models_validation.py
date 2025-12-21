import pytest
from decimal import Decimal
from pydantic import ValidationError
from app.models import BillCreate, BillItemCreate


def test_bill_create_validation():
    # Valid data
    bill = BillCreate(customer_id=1, items=[BillItemCreate(product_id=1, quantity=2)])
    assert bill.customer_id == 1
    assert len(bill.items) == 1


def test_bill_item_validation_quantity():
    # Ensure standard types are correct
    item = BillItemCreate(product_id=1, quantity=5)
    assert item.quantity == 5


def test_bill_missing_items():
    # Pydantic should raise error if required fields are missing
    with pytest.raises(ValidationError):
        BillCreate(customer_id=1)  # Missing items


def test_bill_invalid_types():
    with pytest.raises(ValidationError):
        BillCreate(customer_id="not-an-int", items=[])
