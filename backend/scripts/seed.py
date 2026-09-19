"""Seed demo data for local development and the live demo.

Run from backend/ with the venv active:
    python -m scripts.seed
"""
from decimal import Decimal

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.user import User, UserRole

DEMO_PASSWORD = "Demo@12345"

DEMO_USERS = [
    ("Sales Demo", "sales@demo.com", UserRole.SALES),
    ("Warehouse Demo", "warehouse@demo.com", UserRole.WAREHOUSE),
    ("Accountant Demo", "accountant@demo.com", UserRole.ACCOUNTANT),
    ("Manager Demo", "manager@demo.com", UserRole.MANAGER),
    ("Owner Demo", "owner@demo.com", UserRole.OWNER),
]

DEMO_CUSTOMERS = [
    ("ABC Technologies", "orders@abctech.example", "9876543210", "Chennai, TN"),
    ("Nova Retail Pvt Ltd", "purchasing@novaretail.example", "9876500000", "Bengaluru, KA"),
]

# sku, name, category, unit_price, tax_rate, initial_qty, reorder_point
DEMO_PRODUCTS = [
    ("DELL-LAP-15", "Dell Laptop 15", "Laptops", Decimal("55000.00"), Decimal("0.18"), 27, 15),
    ("WKB-STD", "Wireless Keyboard", "Accessories", Decimal("1200.00"), Decimal("0.18"), 80, 20),
    ("MON-24IN", "24-inch Monitor", "Monitors", Decimal("9500.00"), Decimal("0.18"), 40, 10),
]


def seed_users(db) -> None:
    for name, email, role in DEMO_USERS:
        if db.query(User).filter(User.email == email).first():
            print(f"Skipping user {email} — already exists.")
            continue
        db.add(User(name=name, email=email, password_hash=hash_password(DEMO_PASSWORD), role=role.value, is_active=True))
        print(f"Created user {email} ({role.value})")


def seed_customers(db) -> None:
    for name, email, phone, address in DEMO_CUSTOMERS:
        if db.query(Customer).filter(Customer.email == email).first():
            print(f"Skipping customer {email} — already exists.")
            continue
        db.add(Customer(name=name, email=email, phone=phone, address=address))
        print(f"Created customer {name}")


def seed_products(db) -> None:
    for sku, name, category, price, tax_rate, qty, reorder in DEMO_PRODUCTS:
        if db.query(Product).filter(Product.sku == sku).first():
            print(f"Skipping product {sku} — already exists.")
            continue
        product = Product(sku=sku, name=name, category=category, unit_price=price, tax_rate=tax_rate)
        db.add(product)
        db.flush()
        db.add(Inventory(product_id=product.id, quantity_on_hand=qty, reorder_point=reorder))
        print(f"Created product {name} (stock={qty})")


def run() -> None:
    db = SessionLocal()
    try:
        seed_users(db)
        seed_customers(db)
        seed_products(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print(f"\nDemo password for all accounts: {DEMO_PASSWORD}")