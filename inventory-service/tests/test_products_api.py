from app import crud
from app.models import ProductCreate


def test_list_products_pagination(client, session):
    # Seed data
    for i in range(4):
        crud.create_product(
            session, ProductCreate(name=f"P{i}", price=10.0, quantity=10)
        )

    resp = client.get("/products/?skip=0&limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_get_single_product(client, session):
    created = crud.create_product(
        session, ProductCreate(name="Tablet", price=300.0, quantity=5)
    )
    resp = client.get(f"/products/{created.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == created.id
    assert body["name"] == "Tablet"


def test_create_product_success(client):
    payload = {"name": "New Item", "price": 15.50, "quantity": 100}
    resp = client.post("/products/", json=payload)
    assert resp.status_code == 200  # or 201 if you set status_code=201
    body = resp.json()
    assert body["name"] == "New Item"
    assert "id" in body


def test_create_product_validation_error(client):
    # Negative price should fail
    payload = {"name": "Bad", "price": -5.0, "quantity": 10}
    resp = client.post("/products/", json=payload)
    assert resp.status_code == 422


def test_adjust_stock_endpoint(client, session):
    created = crud.create_product(
        session, ProductCreate(name="StockItem", price=10.0, quantity=50)
    )

    # Decrease stock by 5 via API
    url = f"/products/{created.id}/stock?quantity_delta=-5"
    resp = client.patch(url)

    assert resp.status_code == 200
    body = resp.json()
    assert body["quantity"] == 45

    # Force the session to reload the object from the DB
    session.refresh(created)

    assert created.quantity == 45

def test_get_not_found(client):
    resp = client.get("/products/99999")
    assert resp.status_code == 404
