from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.ai.tool_errors import ToolExecutionError
from app.models.inventory import Inventory
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_rejection import OrderRejection
from app.models.product import Product

_SOLD_STATUSES = [OrderStatus.CONFIRMED.value, OrderStatus.INVOICED.value, OrderStatus.COMPLETED.value]


def get_inventory(db: Session, args: dict) -> dict:
    product_id = args.get("product_id")
    if not isinstance(product_id, int):
        raise ToolExecutionError("INVALID_ARGUMENTS", "product_id must be an integer.")

    product = db.get(Product, product_id)
    if not product:
        raise ToolExecutionError("PRODUCT_NOT_FOUND", f"Product {product_id} does not exist.")

    inv = db.query(Inventory).filter(Inventory.product_id == product.id).first()
    return {
        "product_id": product.id, "product_name": product.name, "sku": product.sku,
        "quantity_on_hand": inv.quantity_on_hand if inv else 0,
        "reorder_point": inv.reorder_point if inv else 0,
    }


def get_low_stock_products(db: Session, args: dict) -> dict:
    rows = (
        db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id)
        .filter(Inventory.quantity_on_hand <= Inventory.reorder_point).all()
    )
    return {
        "products": [
            {"product_id": p.id, "product_name": p.name, "sku": p.sku,
             "quantity_on_hand": i.quantity_on_hand, "reorder_point": i.reorder_point}
            for i, p in rows
        ]
    }


def get_sales_history(db: Session, args: dict) -> dict:
    product_id = args.get("product_id")
    days = args.get("days", 30)
    if not isinstance(product_id, int):
        raise ToolExecutionError("INVALID_ARGUMENTS", "product_id must be an integer.")

    product = db.get(Product, product_id)
    if not product:
        raise ToolExecutionError("PRODUCT_NOT_FOUND", f"Product {product_id} does not exist.")

    since = datetime.now(timezone.utc) - timedelta(days=days)
    units_sold = (
        db.query(func.coalesce(func.sum(OrderItem.quantity), 0))
        .join(Order, OrderItem.order_id == Order.id)
        .filter(OrderItem.product_id == product_id, Order.status.in_(_SOLD_STATUSES), Order.created_at >= since)
        .scalar()
    )
    return {"product_id": product_id, "product_name": product.name, "days": days, "units_sold": int(units_sold)}


def get_inventory_value(db: Session, args: dict) -> dict:
    rows = db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id).all()
    total_value = sum((Decimal(i.quantity_on_hand) * p.unit_price for i, p in rows), Decimal("0.00"))
    return {"total_inventory_value": str(total_value), "product_count": len(rows)}


def get_rejected_orders(db: Session, args: dict) -> dict:
    days = args.get("days", 30)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(OrderRejection, Order).join(Order, OrderRejection.order_id == Order.id)
        .filter(OrderRejection.created_at >= since).all()
    )
    return {
        "days": days, "count": len(rows),
        "orders": [{"order_number": o.order_number, "reason_code": r.reason_code} for r, o in rows],
    }