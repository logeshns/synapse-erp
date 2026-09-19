"""add order/receipt handler columns and manager_ratings table

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("orders", sa.Column("warehouse_handled_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("payment_receipts", sa.Column("generated_by_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))

    op.create_table(
        "manager_ratings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("manager_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("communication", sa.Integer(), nullable=False),
        sa.Column("accuracy", sa.Integer(), nullable=False),
        sa.Column("order_processing", sa.Integer(), nullable=False),
        sa.Column("customer_handling", sa.Integer(), nullable=False),
        sa.Column("overall", sa.Integer(), nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("manager_ratings")
    op.drop_column("payment_receipts", "generated_by_user_id")
    op.drop_column("orders", "warehouse_handled_by_user_id")