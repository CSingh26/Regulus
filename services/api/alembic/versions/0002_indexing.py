"""indexing tables

Revision ID: 0002_indexing
Revises: 0001_init
Create Date: 2025-01-01 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_indexing"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "repo_id", sa.Integer(), sa.ForeignKey("repos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("language", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("loc", sa.Integer(), nullable=False),
        sa.Column("sha", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_files_repo_id", "files", ["repo_id"])
    op.create_index("ix_files_path", "files", ["path"])
    op.create_unique_constraint("uq_files_repo_path", "files", ["repo_id", "path"])

    op.create_table(
        "chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "repo_id", sa.Integer(), sa.ForeignKey("repos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "file_id", sa.Integer(), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_chunks_repo_id", "chunks", ["repo_id"])
    op.create_index("ix_chunks_file_id", "chunks", ["file_id"])


def downgrade() -> None:
    op.drop_index("ix_chunks_file_id", table_name="chunks")
    op.drop_index("ix_chunks_repo_id", table_name="chunks")
    op.drop_table("chunks")

    op.drop_constraint("uq_files_repo_path", "files", type_="unique")
    op.drop_index("ix_files_path", table_name="files")
    op.drop_index("ix_files_repo_id", table_name="files")
    op.drop_table("files")
