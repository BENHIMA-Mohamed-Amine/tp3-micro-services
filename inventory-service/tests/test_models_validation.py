import pytest
from pydantic import ValidationError
from app.models import ProductCreate, ProductUpdate


def test_product_create_validation_negative_price():
    with pytest.raises(ValidationError):
        ProductCreate(name="Bad Price", price=-10.0, quantity=5)


def test_product_create_validation_negative_quantity():
    with pytest.raises(ValidationError):
        ProductCreate(name="Bad Qty", price=10.0, quantity=-1)


def test_product_create_validation_valid():
    # Should not raise
    p = ProductCreate(name="Good", price=10.0, quantity=0)
    assert p.name == "Good"
    assert p.price == 10.0


def test_product_update_optional_fields():
    # No fields provided is allowed (all optional)
    pu = ProductUpdate()
    assert pu.name is None
    assert pu.price is None
    assert pu.quantity is None
