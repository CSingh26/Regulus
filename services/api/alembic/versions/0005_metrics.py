"""metrics snapshots

Revision ID: 0005_metrics
Revises: 0004_embeddings
Create Date: 2025-01-01 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0005_metrics"
down_revision = "0004_embeddings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "metrics_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "repo_id", sa.Integer(), sa.ForeignKey("repos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_metrics_snapshots_repo_id", "metrics_snapshots", ["repo_id"])


def downgrade() -> None:
    op.drop_index("ix_metrics_snapshots_repo_id", table_name="metrics_snapshots")
    op.drop_table("metrics_snapshots")
