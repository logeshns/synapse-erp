from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.product import Product
from app.schemas.ai import ExtractedOrderData


def resolve_extraction(db: Session, data: ExtractedOrderData) -> dict:
    """Deterministic DB matching — the LLM proposes names, this resolves
    them to real IDs or flags them for human review. Never guesses."""
    customer_result = _resolve_customer(db, data.customer_name)
    item_results = [_resolve_product(db, item.product_name, item.quantity) for item in data.items]

    needs_review = (
        customer_result["status"] != "MATCHED"
        or not item_results
        or any(r["status"] != "MATCHED" for r in item_results)
    )

    return {
        "raw_extraction": data.model_dump(),
        "resolution": {"customer": customer_result, "items": item_results},
        "needs_review": needs_review,
    }


def _resolve_customer(db: Session, name: str | None) -> dict:
    if not name:
        return {"status": "NOT_FOUND", "query": None}

    exact = db.query(Customer).filter(func.lower(Customer.name) == name.strip().lower()).first()
    if exact:
        return {"status": "MATCHED", "customer_id": exact.id, "matched_name": exact.name}

    candidates = db.query(Customer).filter(Customer.name.ilike(f"%{name.strip()}%")).limit(5).all()
    if len(candidates) == 1:
        return {"status": "MATCHED", "customer_id": candidates[0].id, "matched_name": candidates[0].name}
    if len(candidates) > 1:
        return {"status": "AMBIGUOUS", "query": name, "candidates": [{"id": c.id, "name": c.name} for c in candidates]}
    return {"status": "NOT_FOUND", "query": name}


def _resolve_product(db: Session, name: str, quantity: int) -> dict:
    exact = (
        db.query(Product)
        .filter(func.lower(Product.name) == name.strip().lower(), Product.is_active.is_(True))
        .first()
    )
    if exact:
        return {"status": "MATCHED", "product_id": exact.id, "matched_name": exact.name, "quantity": quantity}

    candidates = (
        db.query(Product)
        .filter(Product.name.ilike(f"%{name.strip()}%"), Product.is_active.is_(True))
        .limit(5)
        .all()
    )
    if len(candidates) == 1:
        return {"status": "MATCHED", "product_id": candidates[0].id, "matched_name": candidates[0].name, "quantity": quantity}
    if len(candidates) > 1:
        return {
            "status": "AMBIGUOUS",
            "query": name,
            "quantity": quantity,
            "candidates": [{"id": p.id, "name": p.name} for p in candidates],
        }
    return {"status": "NOT_FOUND", "query": name, "quantity": quantity}