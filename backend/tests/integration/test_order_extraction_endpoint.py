def test_extract_success_marks_ai_status_success(client, auth_headers, override_ai_provider):
    class FakeProvider:
        def complete(self, system_prompt, user_prompt, timeout_seconds=20.0):
            return (
                '{"customer_name": "Extract Co", "items": '
                '[{"product_name": "Extract Product", "quantity": 4}], '
                '"requested_delivery_date": null, "notes": null}'
            )

    override_ai_provider(FakeProvider())

    wh = auth_headers("wh_extract@test.com", "WAREHOUSE")
    sales = auth_headers("sales_extract@test.com", "SALES")

    client.post("/customers", json={"name": "Extract Co", "email": "extractco@test.com"}, headers=sales)
    client.post("/products", json={"sku": "EXT-1", "name": "Extract Product", "unit_price": "100.00"}, headers=wh)

    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "Extract Co wants 4 units"}, headers=sales).json()

    response = client.post(f"/order-requests/{req['id']}/extract", headers=sales)

    assert response.status_code == 200
    body = response.json()
    assert body["ai_status"] == "SUCCESS"
    assert body["extracted_data"]["resolution"]["customer"]["status"] == "MATCHED"


def test_extract_failure_is_graceful_not_a_500(client, auth_headers, override_ai_provider):
    class BrokenProvider:
        def complete(self, system_prompt, user_prompt, timeout_seconds=20.0):
            return "definitely not json"

    override_ai_provider(BrokenProvider())

    sales = auth_headers("sales_fail@test.com", "SALES")
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "garbled request"}, headers=sales).json()

    response = client.post(f"/order-requests/{req['id']}/extract", headers=sales)

    assert response.status_code == 200
    assert response.json()["ai_status"] == "FAILED"


def test_cannot_extract_an_already_approved_request(client, auth_headers, override_ai_provider):
    class FakeProvider:
        def complete(self, system_prompt, user_prompt, timeout_seconds=20.0):
            return '{"customer_name": null, "items": [], "requested_delivery_date": null, "notes": null}'

    override_ai_provider(FakeProvider())

    wh = auth_headers("wh_appr@test.com", "WAREHOUSE")
    sales = auth_headers("sales_appr@test.com", "SALES")
    product_id = client.post("/products", json={"sku": "APPR-1", "name": "Appr Product", "unit_price": "50.00"}, headers=wh).json()["id"]
    customer_id = client.post("/customers", json={"name": "Appr Customer", "email": "apprc@test.com"}, headers=sales).json()["id"]

    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales).json()
    client.post(
        f"/order-requests/{req['id']}/approve",
        json={"customer_id": customer_id, "items": [{"product_id": product_id, "quantity": 1}]},
        headers=sales,
    )

    response = client.post(f"/order-requests/{req['id']}/extract", headers=sales)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "INVALID_STATE_FOR_EXTRACTION"