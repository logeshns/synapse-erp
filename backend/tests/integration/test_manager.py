def test_team_overview_counts_confirmed_orders(client, auth_headers, override_ai_provider):
    class FakeProvider:
        def complete(self, s, u, timeout_seconds=20.0):
            return "Rejected."
    override_ai_provider(FakeProvider())

    wh = auth_headers("wh_mgr1@test.com", "WAREHOUSE")
    sales = auth_headers("sales_mgr1@test.com", "SALES")
    manager = auth_headers("manager_mgr1@test.com", "MANAGER")

    product = client.post("/products", json={"sku": "MGR-1", "name": "Manager Test Product", "unit_price": "100.00", "initial_quantity": 10}, headers=wh).json()
    customer = client.post("/customers", json={"name": "Manager Customer", "email": "mgrcust@test.com"}, headers=sales).json()
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales).json()
    order = client.post(f"/order-requests/{req['id']}/approve", json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 2}]}, headers=sales).json()
    client.post(f"/orders/{order['id']}/confirm", headers=wh)

    team = client.get("/manager/team", headers=manager).json()
    assert any(m["role"] == "WAREHOUSE" and (m.get("orders_confirmed") or 0) >= 1 for m in team)


def test_add_and_list_rating(client, auth_headers):
    manager = auth_headers("manager_mgr2@test.com", "MANAGER")
    sales_headers = auth_headers("sales_mgr2@test.com", "SALES")
    me = client.get("/auth/me", headers=sales_headers).json()

    response = client.post(
        "/manager/ratings",
        json={"employee_id": me["id"], "period": "2026-09", "communication": 4, "accuracy": 5,
              "order_processing": 4, "customer_handling": 5, "overall": 4, "comments": "Great work."},
        headers=manager,
    )
    assert response.status_code == 201

    ratings = client.get(f"/manager/ratings?employee_id={me['id']}", headers=manager).json()
    assert len(ratings) == 1