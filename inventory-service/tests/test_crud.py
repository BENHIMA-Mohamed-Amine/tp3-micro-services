import pytest
from app import crud
from app.models import ProductCreate, ProductUpdate


def test_create_and_get_product(session):
    payload = ProductCreate(name="Laptop", price=999.99, quantity=10)
    created = crud.create_product(session, payload)

    assert created.id is not None
    assert created.name == "Laptop"
    assert created.price == 999.99

    fetched = crud.get_product(session, created.id)
    assert fetched.id == created.id


def test_get_products_pagination(session):
    # Create 5 products
    for i in range(5):
        crud.create_product(
            session, ProductCreate(name=f"Prod{i}", price=10.0 + i, quantity=5)
        )

    results = crud.get_products(session, skip=0, limit=2)
    assert len(results) == 2


def test_update_product(session):
    created = crud.create_product(
        session, ProductCreate(name="Phone", price=500.0, quantity=20)
    )

    update_data = ProductUpdate(price=450.0)
    updated = crud.update_product(session, created.id, update_data)

    assert updated.price == 450.0
    assert updated.name == "Phone"  # Unchanged


def test_update_stock_logic(session):
    created = crud.create_product(
        session, ProductCreate(name="Mouse", price=25.0, quantity=100)
    )

    # Add stock
    updated = crud.update_stock(session, created.id, 10)
    assert updated.quantity == 110

    # Remove stock
    updated = crud.update_stock(session, created.id, -20)
    assert updated.quantity == 90
