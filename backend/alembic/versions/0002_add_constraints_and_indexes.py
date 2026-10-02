"""add constraints and indexes

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-02

"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role IN ('admin', 'member')",
    )
    op.create_check_constraint(
        "ck_leads_status",
        "leads",
        "status IN ('new', 'contacted', 'qualified', 'lost')",
    )
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)
    op.create_index("ix_leads_owner_id", "leads", ["owner_id"])


def downgrade():
    op.drop_index("ix_leads_owner_id", table_name="leads")
    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_constraint("ck_leads_status", "leads", type_="check")
    op.drop_constraint("ck_users_role", "users", type_="check")
