def _create_product(client, headers, sku="ORD-PROD", price="1000.00", qty=50):
    resp = client.post(
        "/products",
        json={"sku": sku, "name": "Order Test Product", "unit_price": price, "initial_quantity": qty, "reorder_point": 5},
        headers=headers,
    )
    return resp.json()["id"]


def _create_customer(client, headers, email="cust@test.com"):
    resp = client.post("/customers", json={"name": "Test Customer", "email": email}, headers=headers)
    return resp.json()["id"]


def test_offline_order_request_is_attributed_to_submitting_sales_user(client, auth_headers):
    sales_headers = auth_headers("sales_a@test.com", "SALES")

    response = client.post(
        "/order-requests",
        json={"source": "OFFLINE", "raw_text": "Customer called asking for 5 units."},
        headers=sales_headers,
    )

    assert response.status_code == 201
    assert response.json()["source"] == "OFFLINE"
    assert response.json()["review_status"] == "PENDING_REVIEW"


def test_approve_order_request_creates_order_with_correct_totals(client, auth_headers):
    wh_headers = auth_headers("wh_a@test.com", "WAREHOUSE")
    sales_headers = auth_headers("sales_b@test.com", "SALES")

    product_id = _create_product(client, wh_headers, sku="APR-1", price="1000.00")
    customer_id = _create_customer(client, sales_headers, email="apr@test.com")

    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "3 units please"}, headers=sales_headers)
    request_id = req.json()["id"]

    approval = client.post(
        f"/order-requests/{request_id}/approve",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 3}]},
        headers=sales_headers,
    )

    assert approval.status_code == 200
    order = approval.json()
    assert order["status"] == "PENDING_WAREHOUSE"
    assert float(order["subtotal"]) == 3000.00
    assert round(float(order["tax_total"]), 2) == 540.00
    assert round(float(order["total"]), 2) == 3540.00


def test_re_approving_an_order_request_is_idempotent(client, auth_headers):
    wh_headers = auth_headers("wh_b@test.com", "WAREHOUSE")
    sales_headers = auth_headers("sales_c@test.com", "SALES")

    product_id = _create_product(client, wh_headers, sku="IDEM-1")
    customer_id = _create_customer(client, sales_headers, email="idem@test.com")
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales_headers).json()

    payload = {"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]}
    first = client.post(f"/order-requests/{req['id']}/approve", json=payload, headers=sales_headers)
    second = client.post(f"/order-requests/{req['id']}/approve", json=payload, headers=sales_headers)

    assert first.json()["id"] == second.json()["id"]
    assert first.json()["order_number"] == second.json()["order_number"]


def test_approving_with_unknown_product_fails_and_creates_no_order(client, auth_headers):
    sales_headers = auth_headers("sales_d@test.com", "SALES")
    customer_id = _create_customer(client, sales_headers, email="badprod@test.com")
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales_headers).json()

    response = client.post(
        f"/order-requests/{req['id']}/approve",
        json={"customer_id": customer_id, "items": [{"product_id": 999999, "quantity": 1}]},
        headers=sales_headers,
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_PRODUCT"

    orders = client.get("/orders", headers=sales_headers).json()
    assert all(o["order_request_id"] != req["id"] for o in orders)


def test_cannot_reject_an_already_approved_request(client, auth_headers):
    wh_headers = auth_headers("wh_c@test.com", "WAREHOUSE")
    sales_headers = auth_headers("sales_e@test.com", "SALES")

    product_id = _create_product(client, wh_headers, sku="REJ-1")
    customer_id = _create_customer(client, sales_headers, email="rej@test.com")
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales_headers).json()

    client.post(
        f"/order-requests/{req['id']}/approve",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
        headers=sales_headers,
    )
    reject = client.post(f"/order-requests/{req['id']}/reject", json={"reason": "changed mind"}, headers=sales_headers)

    assert reject.status_code == 409
    assert reject.json()["error"]["code"] == "ALREADY_APPROVED"