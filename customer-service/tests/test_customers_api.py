from fastapi.testclient import TestClient

from app.main import app


import pytest
from app import crud
from app.models import CustomerCreate


def test_list_customers_pagination(client, session):
    # Seed data
    for i in range(4):
        crud.create_customer(
            session, CustomerCreate(name=f"C{i}", email=f"c{i}@ex.com")
        )

    resp = client.get("/api/customers?skip=0&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_single_customer(client, session):
    created = crud.create_customer(
        session, CustomerCreate(name="Sam", email="sam@ex.com")
    )
    resp = client.get(f"/api/customers/{created.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == created.id
    assert body["name"] == "Sam"


def test_get_not_found(client):
    resp = client.get("/api/customers/99999")
    assert resp.status_code == 404


def test_create_customer_success(client, session):
    payload = {"name": "New", "email": "new@ex.com"}
    resp = client.post("/api/customers", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == payload["name"]
    assert "id" in body


def test_create_customer_validation_error(client):
    payload = {"name": "", "email": "not-an-email"}
    resp = client.post("/api/customers", json=payload)
    assert resp.status_code == 422


def test_create_duplicate_email(client, session):
    crud.create_customer(session, CustomerCreate(name="A", email="dup@ex.com"))
    resp = client.post("/api/customers", json={"name": "B", "email": "dup@ex.com"})
    assert resp.status_code == 400
    assert "Error creating customer" in resp.json().get("detail", "")


def test_update_customer(client, session):
    created = crud.create_customer(
        session, CustomerCreate(name="Up", email="up@ex.com")
    )
    resp = client.put(f"/api/customers/{created.id}", json={"name": "Updated"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Updated"


def test_update_not_found(client):
    resp = client.put("/api/customers/99999", json={"name": "Nope"})
    assert resp.status_code == 404


def test_delete_customer(client, session):
    created = crud.create_customer(session, CustomerCreate(name="D", email="d@ex.com"))
    resp = client.delete(f"/api/customers/{created.id}")
    assert resp.status_code == 204
    # Verify it's gone
    get_resp = client.get(f"/api/customers/{created.id}")
    assert get_resp.status_code == 404
