from app.ai.resolution import resolve_extraction
from app.models.customer import Customer
from app.models.product import Product
from app.schemas.ai import ExtractedOrderData, ExtractedOrderItem


def test_resolves_exact_matches_as_matched(db_session):
    db_session.add(Customer(name="ABC Technologies", email="abc@test.com"))
    db_session.add(Product(sku="P1", name="Dell Laptop", unit_price=1000))
    db_session.commit()

    data = ExtractedOrderData(
        customer_name="ABC Technologies", items=[ExtractedOrderItem(product_name="Dell Laptop", quantity=3)]
    )
    resolved = resolve_extraction(db_session, data)

    assert resolved["resolution"]["customer"]["status"] == "MATCHED"
    assert resolved["resolution"]["items"][0]["status"] == "MATCHED"
    assert resolved["needs_review"] is False


def test_ambiguous_product_name_needs_review(db_session):
    db_session.add(Product(sku="P1", name="Dell Laptop 15", unit_price=1000))
    db_session.add(Product(sku="P2", name="Dell Laptop 13", unit_price=1200))
    db_session.commit()

    data = ExtractedOrderData(customer_name=None, items=[ExtractedOrderItem(product_name="Dell Laptop", quantity=1)])
    resolved = resolve_extraction(db_session, data)

    assert resolved["resolution"]["items"][0]["status"] == "AMBIGUOUS"
    assert resolved["needs_review"] is True


def test_unknown_product_is_not_found(db_session):
    data = ExtractedOrderData(customer_name=None, items=[ExtractedOrderItem(product_name="Nonexistent Widget", quantity=1)])
    resolved = resolve_extraction(db_session, data)

    assert resolved["resolution"]["items"][0]["status"] == "NOT_FOUND"
    assert resolved["needs_review"] is True