"""initial tables

Revision ID: 0001
Revises:
Create Date: 2026-10-02

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("role", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("company", sa.String, nullable=False),
        sa.Column("website", sa.String, nullable=True),
        sa.Column("status", sa.String, nullable=False, server_default="new"),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("token_hash", sa.String, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("revoked_at", sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table("refresh_tokens")
    op.drop_table("leads")
    op.drop_table("users")
