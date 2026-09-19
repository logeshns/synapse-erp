import hashlib
import hmac
import json
import time

from app.core.config import settings


def _stripe_signature(payload: bytes, secret: str) -> str:
    timestamp = int(time.time())
    signed_payload = f"{timestamp}.{payload.decode()}"
    signature = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


def _checkout_completed_event(event_id, invoice_id, amount_total_paise):
    return {
        "id": event_id, "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test_123", "payment_intent": "pi_test_123",
                             "amount_total": amount_total_paise, "metadata": {"invoice_id": str(invoice_id)}}},
    }


def _confirmed_and_invoiced_order(client, wh, sales, sku="PAY-1"):
    product = client.post("/products", json={"sku": sku, "name": "Pay Product", "unit_price": "1000.00", "initial_quantity": 10}, headers=wh).json()
    customer = client.post("/customers", json={"name": "Pay Customer", "email": f"{sku.lower()}@test.com"}, headers=sales).json()
    req = client.post("/order-requests", json={"source": "OFFLINE", "raw_text": "test"}, headers=sales).json()
    order = client.post(f"/order-requests/{req['id']}/approve",
                         json={"customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": 1}]},
                         headers=sales).json()
    client.post(f"/orders/{order['id']}/confirm", headers=wh)
    invoice = client.post(f"/invoices/generate/{order['id']}", headers=wh).json()
    return order, invoice


def test_webhook_rejects_bad_signature(client, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    payload = json.dumps(_checkout_completed_event("evt_bad_sig", 1, 100000)).encode()

    response = client.post("/payments/webhook", content=payload,
                            headers={"stripe-signature": "t=1,v1=deadbeef", "content-type": "application/json"})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "PAYMENT_WEBHOOK_INVALID"


def test_webhook_marks_invoice_paid_and_order_completed(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    wh, sales = auth_headers("wh_pay1@test.com", "WAREHOUSE"), auth_headers("sales_pay1@test.com", "SALES")
    order, invoice = _confirmed_and_invoiced_order(client, wh, sales, sku="PAY-OK")

    payload = json.dumps(_checkout_completed_event("evt_ok_1", invoice["id"], int(float(invoice["total"]) * 100))).encode()
    signature = _stripe_signature(payload, "whsec_test_secret")

    response = client.post("/payments/webhook", content=payload,
                            headers={"stripe-signature": signature, "content-type": "application/json"})
    assert response.status_code == 200

    assert client.get(f"/invoices/{invoice['id']}", headers=wh).json()["status"] == "PAID"
    assert client.get(f"/orders/{order['id']}", headers=wh).json()["status"] == "COMPLETED"


def test_duplicate_webhook_event_does_not_duplicate_payment(client, auth_headers, monkeypatch):
    monkeypatch.setattr(settings, "STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
    wh, sales = auth_headers("wh_pay2@test.com", "WAREHOUSE"), auth_headers("sales_pay2@test.com", "SALES")
    order, invoice = _confirmed_and_invoiced_order(client, wh, sales, sku="PAY-DUP")

    payload = json.dumps(_checkout_completed_event("evt_dup_1", invoice["id"], int(float(invoice["total"]) * 100))).encode()
    signature = _stripe_signature(payload, "whsec_test_secret")
    headers = {"stripe-signature": signature, "content-type": "application/json"}

    client.post("/payments/webhook", content=payload, headers=headers)
    client.post("/payments/webhook", content=payload, headers=headers)

    acct = auth_headers("acct_dup@test.com", "ACCOUNTANT")
    payments = [p for p in client.get("/payments", headers=acct).json() if p["invoice_id"] == invoice["id"]]
    assert len(payments) == 1