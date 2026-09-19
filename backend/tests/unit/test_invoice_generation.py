def _confirmed_order(client, wh, sales, sku="INV-1"):
    product = client.post("/products", json={"sku": sku, "name": "Invoice Product", "unit_price": "500.00",
                                               "initial_quantity": 20, "reorder_point": 2}, headers=wh).json()
    customer = client.post("/customers", json={"name": "Invoice Customer", "email": f"{sku.lower()}@test.com"}, headers=sales).json()
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales).json()
    order = client.post(f"/order-requests/{req['id']}/approve",
                         json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 2}]},
                         headers=sales).json()
    client.post(f"/orders/{order['id']}/confirm", headers=wh)
    return order


def test_generate_invoice_from_confirmed_order(client, auth_headers):
    wh, sales = auth_headers("wh_inv1@test.com", "WAREHOUSE"), auth_headers("sales_inv1@test.com", "SALES")
    order = _confirmed_order(client, wh, sales, sku="INV-GEN")

    response = client.post(f"/invoices/generate/{order['id']}", headers=wh)
    assert response.status_code == 201
    invoice = response.json()
    assert invoice["status"] == "UNPAID"
    assert round(float(invoice["total"]), 2) == round(1000.00 * 1.18, 2)

    order_after = client.get(f"/orders/{order['id']}", headers=wh).json()
    assert order_after["status"] == "INVOICED"


def test_generate_invoice_is_idempotent(client, auth_headers):
    wh, sales = auth_headers("wh_inv2@test.com", "WAREHOUSE"), auth_headers("sales_inv2@test.com", "SALES")
    order = _confirmed_order(client, wh, sales, sku="INV-IDEM")

    first = client.post(f"/invoices/generate/{order['id']}", headers=wh)
    second = client.post(f"/invoices/generate/{order['id']}", headers=wh)
    assert first.json()["invoice_number"] == second.json()["invoice_number"]


def test_cannot_generate_invoice_for_unconfirmed_order(client, auth_headers):
    wh, sales = auth_headers("wh_inv3@test.com", "WAREHOUSE"), auth_headers("sales_inv3@test.com", "SALES")
    product = client.post("/products", json={"sku": "INV-NOTCONF", "name": "X", "unit_price": "10.00", "initial_quantity": 5}, headers=wh).json()
    customer = client.post("/customers", json={"name": "X Customer", "email": "invnotconf@test.com"}, headers=sales).json()
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales).json()
    order = client.post(f"/order-requests/{req['id']}/approve",
                         json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 1}]},
                         headers=sales).json()

    response = client.post(f"/invoices/generate/{order['id']}", headers=wh)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_ORDER_STATE"