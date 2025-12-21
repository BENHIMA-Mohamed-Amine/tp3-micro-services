def test_create_bill_api(client, mock_external_clients):
    payload = {"customer_id": 1, "items": [{"product_id": 10, "quantity": 1}]}

    response = client.post("/api/bills", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == 1
    assert float(data["total_amount"]) == 10.0  # Mocked price (10.0) * 1


def test_get_bill_api(client, mock_external_clients):
    # 1. Create a bill first
    payload = {"customer_id": 1, "items": [{"product_id": 10, "quantity": 2}]}
    create_resp = client.post("/api/bills", json=payload)
    bill_id = create_resp.json()["id"]

    # 2. Fetch it
    response = client.get(f"/api/bills/{bill_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == bill_id
    assert len(data["items"]) == 1
    assert float(data["total_amount"]) == 20.0


def test_get_bill_not_found(client):
    response = client.get("/api/bills/99999")
    assert (
        response.status_code == 404
    )  # Depends on your router implementation, usually returns null or 404


def test_list_bills_pagination(client, mock_external_clients):
    # 1. Create 3 bills
    # We reuse the mocked client which always returns valid products/customers
    payload = {"customer_id": 1, "items": [{"product_id": 10, "quantity": 1}]}

    for _ in range(3):
        client.post("/api/bills", json=payload)

    # 2. Test default limit
    resp = client.get("/api/bills")
    assert resp.status_code == 200
    assert len(resp.json()) == 3

    # 3. Test pagination (limit 2)
    resp_limit = client.get("/api/bills?limit=2")
    assert len(resp_limit.json()) == 2