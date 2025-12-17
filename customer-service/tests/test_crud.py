import pytest

from app import crud
from app.models import CustomerCreate, Customer


def test_create_get_update_delete_customer(session):
    # create
    data = CustomerCreate(name="Alice", email="alice@example.com")
    customer = crud.create_customer(session, data)
    assert customer.id is not None
    assert customer.name == "Alice"

    # get
    got = crud.get_customer(session, customer.id)
    assert got is not None
    assert got.email == "alice@example.com"

    # update
    update = Customer(name="Alice B", email="aliceb@example.com")
    updated = crud.update_customer(session, customer.id, update)
    assert updated.name == "Alice B"

    # delete
    deleted = crud.delete_customer(session, customer.id)
    assert deleted is True
    assert crud.get_customer(session, customer.id) is None


def test_get_customers_pagination(session):
    # create 3
    for i in range(3):
        crud.create_customer(
            session, CustomerCreate(name=f"U{i}", email=f"u{i}@example.com")
        )

    lst = crud.get_customers(session, skip=0, limit=2)
    assert len(lst) == 2


from app import crud
from app.models import CustomerCreate


def test_create_and_get_customer(session):
    payload = CustomerCreate(name="Alice", email="alice@example.com")
    created = crud.create_customer(session, payload)
    assert created.id is not None
    assert created.name == "Alice"
    assert created.email == "alice@example.com"

    fetched = crud.get_customer(session, created.id)
    assert fetched.id == created.id


def test_get_customers_pagination(session):
    # Clear any existing
    # Create 5 customers
    for i in range(5):
        crud.create_customer(
            session, CustomerCreate(name=f"User{i}", email=f"user{i}@example.com")
        )

    results = crud.get_customers(session, skip=0, limit=2)
    assert len(results) == 2


def test_update_and_delete_customer(session):
    created = crud.create_customer(
        session, CustomerCreate(name="Bob", email="bob@example.com")
    )

    # Partial update
    from app.models import CustomerUpdate

    update_data = CustomerUpdate(name="Bobby")
    updated = crud.update_customer(session, created.id, update_data)
    assert updated.name == "Bobby"
    assert updated.email == "bob@example.com"

    # Delete
    ok = crud.delete_customer(session, created.id)
    assert ok is True

    # Delete non-existent
    ok2 = crud.delete_customer(session, 9999)
    assert ok2 is False
