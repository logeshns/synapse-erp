def test_create_product_also_creates_inventory_row(client, auth_headers):
    headers = auth_headers("warehouse@test.com", "WAREHOUSE")

    response = client.post(
        "/products",
        json={"sku": "TEST-001", "name": "Test Widget", "unit_price": "100.00", "initial_quantity": 25, "reorder_point": 5},
        headers=headers,
    )
    assert response.status_code == 201
    product_id = response.json()["id"]

    inventory = client.get("/inventory", headers=headers).json()
    match = next(i for i in inventory if i["product_id"] == product_id)
    assert match["quantity_on_hand"] == 25
    assert match["reorder_point"] == 5


def test_duplicate_sku_is_rejected(client, auth_headers):
    headers = auth_headers("warehouse2@test.com", "WAREHOUSE")
    payload = {"sku": "DUP-001", "name": "Widget", "unit_price": "50.00"}

    first = client.post("/products", json=payload, headers=headers)
    second = client.post("/products", json=payload, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "DUPLICATE_SKU"


def test_sales_cannot_create_products(client, auth_headers):
    headers = auth_headers("sales1@test.com", "SALES")
    response = client.post("/products", json={"sku": "X-1", "name": "X", "unit_price": "10.00"}, headers=headers)
    assert response.status_code == 403


def test_low_stock_endpoint_filters_correctly(client, auth_headers):
    headers = auth_headers("warehouse3@test.com", "WAREHOUSE")
    client.post(
        "/products",
        json={"sku": "LOW-1", "name": "Low Stock Item", "unit_price": "10.00", "initial_quantity": 2, "reorder_point": 10},
        headers=headers,
    )
    client.post(
        "/products",
        json={"sku": "HIGH-1", "name": "Well Stocked Item", "unit_price": "10.00", "initial_quantity": 100, "reorder_point": 10},
        headers=headers,
    )

    low_stock = client.get("/inventory/low-stock", headers=headers).json()
    skus = {i["sku"] for i in low_stock}
    assert "LOW-1" in skus
    assert "HIGH-1" not in skus