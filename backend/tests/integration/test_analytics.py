import hashlib
import hmac
import json
import time

from app.core.config import settings


def _paid_order(client, wh, sales, sku="AN-1", price="1000.00", qty=2):
    product = client.post("/products", json={"sku": sku, "name": "Analytics Product", "unit_price": price, "initial_quantity": 20}, headers=wh).json()
    customer = client.post("/customers", json={"name": "Analytics Customer", "email": f"{sku.lower()}@test.com"}, headers=sales).json()
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales).json()
    order = client.post(f"/order-requests/{req['id']}/approve", json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": qty}]}, headers=sales).json()
    client.post(f"/orders/{order['id']}/confirm", headers=wh)
    invoice = client.post(f"/invoices/generate/{order['id']}", headers=wh).json()
    return order, invoice


def _pay(client, invoice, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    event = {"id": f"evt_{invoice['id']}", "type": "checkout.session.completed",
              "data": {"object": {"id": "cs_1", "payment_intent": "pi_1", "amount_total": int(float(invoice["total"]) * 100),
                                    "metadata": {"invoice_id": str(invoice["id"])}}}}
    payload = json.dumps(event).encode()
    timestamp = int(time.time())
    signed = f"{timestamp}.{payload.decode()}"
    sig = hmac.new(b"whsec_test_secret", signed.encode(), hashlib.sha256).hexdigest()
    client.post("/payments/webhook", content=payload, headers={"stripe-signature": f"t={timestamp},v1={sig}", "content-type": "application/json"})


def test_revenue_reflects_paid_invoices(client, auth_headers, monkeypatch):
    wh, sales = auth_headers("wh_an1@test.com", "WAREHOUSE"), auth_headers("sales_an1@test.com", "SALES")
    owner = auth_headers("owner_an1@test.com", "OWNER")
    _, invoice = _paid_order(client, wh, sales, sku="AN-REV", price="1000.00", qty=2)
    _pay(client, invoice, monkeypatch)

    response = client.get("/analytics/revenue", headers=owner)
    assert response.status_code == 200
    assert float(response.json()["total_revenue"]) >= float(invoice["total"])


def test_lost_revenue_counts_insufficient_stock_rejections(client, auth_headers, override_ai_provider):
    class FakeProvider:
        def complete(self, s, u, timeout_seconds=20.0):
            return "Rejected due to stock shortage."
    override_ai_provider(FakeProvider())

    wh, sales = auth_headers("wh_an2@test.com", "WAREHOUSE"), auth_headers("sales_an2@test.com", "SALES")
    owner = auth_headers("owner_an2@test.com", "OWNER")

    product = client.post("/products", json={"sku": "AN-LOST", "name": "Lost Product", "unit_price": "500.00", "initial_quantity": 2}, headers=wh).json()
    customer = client.post("/customers", json={"name": "Lost Customer", "email": "anlost@test.com"}, headers=sales).json()
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales).json()
    order = client.post(f"/order-requests/{req['id']}/approve", json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 20}]}, headers=sales).json()
    client.post(f"/orders/{order['id']}/reject", json={"reason_code": "INSUFFICIENT_STOCK"}, headers=wh)

    response = client.get("/analytics/lost-revenue", headers=owner)
    assert response.status_code == 200
    body = response.json()
    assert body["order_count"] >= 1
    assert float(body["total_lost_value"]) >= float(order["total"])