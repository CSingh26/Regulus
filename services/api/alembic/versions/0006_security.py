"""security scans

Revision ID: 0006_security
Revises: 0005_metrics
Create Date: 2025-01-01 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0006_security"
down_revision = "0005_metrics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "repo_id", sa.Integer(), sa.ForeignKey("repos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("tool", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.JSON(), nullable=True),
    )
    op.create_index("ix_scans_repo_id", "scans", ["repo_id"])

    op.create_table(
        "findings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "scan_id", sa.Integer(), sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "repo_id", sa.Integer(), sa.ForeignKey("repos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("tool", sa.String(), nullable=False),
        sa.Column("severity", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("line", sa.Integer(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("rule_id", sa.String(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_findings_repo_id", "findings", ["repo_id"])
    op.create_index("ix_findings_scan_id", "findings", ["scan_id"])


def downgrade() -> None:
    op.drop_index("ix_findings_scan_id", table_name="findings")
    op.drop_index("ix_findings_repo_id", table_name="findings")
    op.drop_table("findings")

    op.drop_index("ix_scans_repo_id", table_name="scans")
    op.drop_table("scans")
