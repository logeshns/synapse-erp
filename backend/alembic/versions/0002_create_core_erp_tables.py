"""create core erp tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_customers_email", "customers", ["email"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 4), nullable=False, server_default="0.18"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)

    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity_on_hand", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reorder_point", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_inventory_product_id", "inventory", ["product_id"])

    op.create_table(
        "order_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_number", sa.String(length=30), nullable=False),
        sa.Column("source", sa.String(length=10), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=True),
        sa.Column("submitted_by_sales_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("ai_status", sa.String(length=20), nullable=False, server_default="NOT_STARTED"),
        sa.Column("extracted_data", sa.JSON(), nullable=True),
        sa.Column("review_status", sa.String(length=20), nullable=False, server_default="PENDING_REVIEW"),
        sa.Column("rejection_reason", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_order_requests_request_number", "order_requests", ["request_number"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_number", sa.String(length=30), nullable=False),
        sa.Column("order_request_id", sa.Integer(), sa.ForeignKey("order_requests.id"), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("source", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PENDING_WAREHOUSE"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("tax_total", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("discount_total", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("total", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_orders_order_number", "orders", ["order_number"])
    op.create_unique_constraint("uq_orders_order_request_id", "orders", ["order_request_id"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_snapshot", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_rate_snapshot", sa.Numeric(5, 4), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False, server_default="0.00"),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_constraint("uq_orders_order_request_id", "orders", type_="unique")
    op.drop_constraint("uq_orders_order_number", "orders", type_="unique")
    op.drop_table("orders")
    op.drop_constraint("uq_order_requests_request_number", "order_requests", type_="unique")
    op.drop_table("order_requests")
    op.drop_constraint("uq_inventory_product_id", "inventory", type_="unique")
    op.drop_table("inventory")
    op.drop_index("ix_products_sku", table_name="products")
    op.drop_table("products")
    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_table("customers")