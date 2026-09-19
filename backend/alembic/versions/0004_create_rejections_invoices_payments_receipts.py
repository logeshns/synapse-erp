"""create order_rejections, invoices, payments, payment_receipts tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "order_rejections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("reason_code", sa.String(length=30), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("ai_explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_order_rejections_order_id", "order_rejections", ["order_id"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("invoice_number", sa.String(length=30), nullable=False),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount_total", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="UNPAID"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_invoices_invoice_number", "invoices", ["invoice_number"])
    op.create_unique_constraint("uq_invoices_order_id", "invoices", ["order_id"])

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("invoices.id"), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False, server_default="stripe"),
        sa.Column("provider_reference", sa.String(length=255), nullable=True),
        sa.Column("stripe_event_id", sa.String(length=255), nullable=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_payments_stripe_event_id", "payments", ["stripe_event_id"])

    op.create_table(
        "payment_receipts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("payment_id", sa.Integer(), sa.ForeignKey("payments.id"), nullable=False),
        sa.Column("receipt_number", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_payment_receipts_payment_id", "payment_receipts", ["payment_id"])
    op.create_unique_constraint("uq_payment_receipts_receipt_number", "payment_receipts", ["receipt_number"])


def downgrade() -> None:
    op.drop_table("payment_receipts")
    op.drop_constraint("uq_payments_stripe_event_id", "payments", type_="unique")
    op.drop_table("payments")
    op.drop_constraint("uq_invoices_order_id", "invoices", type_="unique")
    op.drop_constraint("uq_invoices_invoice_number", "invoices", type_="unique")
    op.drop_table("invoices")
    op.drop_constraint("uq_order_rejections_order_id", "order_rejections", type_="unique")
    op.drop_table("order_rejections")