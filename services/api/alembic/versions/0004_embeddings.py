"""embeddings tables

Revision ID: 0004_embeddings
Revises: 0003_graph
Create Date: 2025-01-01 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision = "0004_embeddings"
down_revision = "0003_graph"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "embeddings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "repo_id", sa.Integer(), sa.ForeignKey("repos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "chunk_id", sa.Integer(), sa.ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("dim", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_embeddings_repo_id", "embeddings", ["repo_id"])
    op.create_index("ix_embeddings_chunk_id", "embeddings", ["chunk_id"])
    op.create_index(
        "ix_embeddings_vector",
        "embeddings",
        ["embedding"],
        postgresql_using="ivfflat",
        postgresql_with={"lists": 100},
    )


def downgrade() -> None:
    op.drop_index("ix_embeddings_vector", table_name="embeddings")
    op.drop_index("ix_embeddings_chunk_id", table_name="embeddings")
    op.drop_index("ix_embeddings_repo_id", table_name="embeddings")
    op.drop_table("embeddings")
