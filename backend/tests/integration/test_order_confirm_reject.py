def _setup_order(client, wh, sales, qty_ordered=5, stock=10, sku="CONF-1"):
    product = client.post("/products", json={"sku": sku, "name": "Confirm Test Product", "unit_price": "100.00",
                                               "initial_quantity": stock, "reorder_point": 2}, headers=wh).json()
    customer = client.post("/customers", json={"name": "Confirm Customer", "email": f"{sku.lower()}@test.com"}, headers=sales).json()
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales).json()
    order = client.post(f"/order-requests/{req['id']}/approve",
                         json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": qty_ordered}]},
                         headers=sales).json()
    return product, order


def test_confirm_deducts_stock(client, auth_headers):
    wh, sales = auth_headers("wh_conf1@test.com", "WAREHOUSE"), auth_headers("sales_conf1@test.com", "SALES")
    product, order = _setup_order(client, wh, sales, qty_ordered=4, stock=10, sku="CONF-DEDUCT")

    response = client.post(f"/orders/{order['id']}/confirm", headers=wh)
    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"

    inv = next(i for i in client.get("/inventory", headers=wh).json() if i["product_id"] == product["id"])
    assert inv["quantity_on_hand"] == 6


def test_confirm_is_idempotent(client, auth_headers):
    wh, sales = auth_headers("wh_conf2@test.com", "WAREHOUSE"), auth_headers("sales_conf2@test.com", "SALES")
    product, order = _setup_order(client, wh, sales, qty_ordered=2, stock=10, sku="CONF-IDEM")

    client.post(f"/orders/{order['id']}/confirm", headers=wh)
    client.post(f"/orders/{order['id']}/confirm", headers=wh)

    inv = next(i for i in client.get("/inventory", headers=wh).json() if i["product_id"] == product["id"])
    assert inv["quantity_on_hand"] == 8  # deducted only once


def test_confirm_blocks_on_insufficient_stock(client, auth_headers):
    wh, sales = auth_headers("wh_conf3@test.com", "WAREHOUSE"), auth_headers("sales_conf3@test.com", "SALES")
    product, order = _setup_order(client, wh, sales, qty_ordered=50, stock=5, sku="CONF-SHORT")

    response = client.post(f"/orders/{order['id']}/confirm", headers=wh)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INSUFFICIENT_STOCK"

    inv = next(i for i in client.get("/inventory", headers=wh).json() if i["product_id"] == product["id"])
    assert inv["quantity_on_hand"] == 5  # unchanged


def test_reject_with_insufficient_stock(client, auth_headers, override_ai_provider):
    class FakeProvider:
        def complete(self, s, u, timeout_seconds=20.0):
            return "This order could not be fulfilled due to a stock shortfall."
    override_ai_provider(FakeProvider())

    wh, sales = auth_headers("wh_rej1@test.com", "WAREHOUSE"), auth_headers("sales_rej1@test.com", "SALES")
    product, order = _setup_order(client, wh, sales, qty_ordered=50, stock=5, sku="REJ-SHORT")

    response = client.post(f"/orders/{order['id']}/reject", json={"reason_code": "INSUFFICIENT_STOCK"}, headers=wh)
    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"

    inv = next(i for i in client.get("/inventory", headers=wh).json() if i["product_id"] == product["id"])
    assert inv["quantity_on_hand"] == 5  # untouched by rejection


def test_reject_falls_back_when_ai_fails(client, auth_headers, override_ai_provider):
    from app.exceptions import AIProviderException

    class BrokenProvider:
        def complete(self, s, u, timeout_seconds=20.0):
            raise AIProviderException("provider down")
    override_ai_provider(BrokenProvider())

    wh, sales = auth_headers("wh_rej2@test.com", "WAREHOUSE"), auth_headers("sales_rej2@test.com", "SALES")
    _, order = _setup_order(client, wh, sales, qty_ordered=20, stock=3, sku="REJ-FALLBACK")

    response = client.post(f"/orders/{order['id']}/reject", json={"reason_code": "INSUFFICIENT_STOCK"}, headers=wh)
    assert response.status_code == 200  # never a 500 just because the LLM is down
    assert response.json()["status"] == "REJECTED"


def test_cannot_confirm_a_rejected_order(client, auth_headers, override_ai_provider):
    class FakeProvider:
        def complete(self, s, u, timeout_seconds=20.0):
            return "Rejected."
    override_ai_provider(FakeProvider())

    wh, sales = auth_headers("wh_rej3@test.com", "WAREHOUSE"), auth_headers("sales_rej3@test.com", "SALES")
    _, order = _setup_order(client, wh, sales, qty_ordered=20, stock=3, sku="REJ-THEN-CONFIRM")

    client.post(f"/orders/{order['id']}/reject", json={"reason_code": "INSUFFICIENT_STOCK"}, headers=wh)
    response = client.post(f"/orders/{order['id']}/confirm", headers=wh)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_ORDER_STATE"