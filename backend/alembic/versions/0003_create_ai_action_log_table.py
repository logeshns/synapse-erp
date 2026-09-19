"""create ai_action_log table

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_action_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("agent_name", sa.String(length=50), nullable=False),
        sa.Column("request_text", sa.Text(), nullable=True),
        sa.Column("model_name", sa.String(length=100), nullable=False),
        sa.Column("tool_calls", sa.JSON(), nullable=True),
        sa.Column("structured_output", sa.JSON(), nullable=True),
        sa.Column("human_decision", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("error", sa.String(length=1000), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("ai_action_log")