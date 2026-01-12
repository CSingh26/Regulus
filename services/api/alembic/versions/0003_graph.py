"""graph tables

Revision ID: 0003_graph
Revises: 0002_indexing
Create Date: 2025-01-01 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_graph"
down_revision = "0002_indexing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "graph_nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "repo_id", sa.Integer(), sa.ForeignKey("repos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "file_id", sa.Integer(), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("path", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("loc", sa.Integer(), nullable=False),
    )
    op.create_index("ix_graph_nodes_repo_id", "graph_nodes", ["repo_id"])
    op.create_index("ix_graph_nodes_file_id", "graph_nodes", ["file_id"])

    op.create_table(
        "graph_edges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "repo_id", sa.Integer(), sa.ForeignKey("repos.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "from_node_id",
            sa.Integer(),
            sa.ForeignKey("graph_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "to_node_id",
            sa.Integer(),
            sa.ForeignKey("graph_nodes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_graph_edges_repo_id", "graph_edges", ["repo_id"])
    op.create_index("ix_graph_edges_from", "graph_edges", ["from_node_id"])
    op.create_index("ix_graph_edges_to", "graph_edges", ["to_node_id"])


def downgrade() -> None:
    op.drop_index("ix_graph_edges_to", table_name="graph_edges")
    op.drop_index("ix_graph_edges_from", table_name="graph_edges")
    op.drop_index("ix_graph_edges_repo_id", table_name="graph_edges")
    op.drop_table("graph_edges")

    op.drop_index("ix_graph_nodes_file_id", table_name="graph_nodes")
    op.drop_index("ix_graph_nodes_repo_id", table_name="graph_nodes")
    op.drop_table("graph_nodes")
