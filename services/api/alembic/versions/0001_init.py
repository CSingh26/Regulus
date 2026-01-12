"""initial schema

Revision ID: 0001_init
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "repos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("index_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("graph_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("embedding_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("security_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("metrics_status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("last_error", sa.Text(), nullable=True),
    )
    op.create_unique_constraint("uq_repos_path", "repos", ["path"])


def downgrade() -> None:
    op.drop_constraint("uq_repos_path", "repos", type_="unique")
    op.drop_table("repos")
