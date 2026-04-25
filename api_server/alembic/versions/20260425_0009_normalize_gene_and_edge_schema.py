"""normalize gene and edge schema

Revision ID: 20260425_0009
Revises: 20260425_0008
Create Date: 2026-04-25

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260425_0009"
down_revision: Union[str, None] = "20260425_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM territory_edges
        WHERE source_id = target_id
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                LEAST(source_id, target_id) AS norm_source_id,
                GREATEST(source_id, target_id) AS norm_target_id,
                ROW_NUMBER() OVER (
                    PARTITION BY LEAST(source_id, target_id), GREATEST(source_id, target_id)
                    ORDER BY id
                ) AS rn
            FROM territory_edges
        )
        DELETE FROM territory_edges te
        USING ranked
        WHERE te.id = ranked.id
          AND ranked.rn > 1
        """
    )
    op.execute(
        """
        UPDATE territory_edges
        SET
            source_id = LEAST(source_id, target_id),
            target_id = GREATEST(source_id, target_id)
        WHERE source_id > target_id
        """
    )

    op.execute(
        """
        DELETE FROM gene_edges
        WHERE source_id = target_id
        """
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                source_id,
                target_id,
                ROW_NUMBER() OVER (
                    PARTITION BY source_id, target_id
                    ORDER BY id
                ) AS rn
            FROM gene_edges
        )
        DELETE FROM gene_edges ge
        USING ranked
        WHERE ge.id = ranked.id
          AND ranked.rn > 1
        """
    )

    op.drop_index(op.f("ix_genes_name"), table_name="genes")
    op.drop_column("genes", "name")

    op.create_check_constraint(
        "ck_gene_edges_not_self",
        "gene_edges",
        "source_id != target_id",
    )
    op.create_unique_constraint(
        "uq_gene_edges_source_target",
        "gene_edges",
        ["source_id", "target_id"],
    )
    op.create_check_constraint(
        "ck_territory_edges_canonical_order",
        "territory_edges",
        "source_id < target_id",
    )
    op.create_unique_constraint(
        "uq_territory_edges_source_target",
        "territory_edges",
        ["source_id", "target_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_territory_edges_source_target", "territory_edges", type_="unique")
    op.drop_constraint("ck_territory_edges_canonical_order", "territory_edges", type_="check")
    op.drop_constraint("uq_gene_edges_source_target", "gene_edges", type_="unique")
    op.drop_constraint("ck_gene_edges_not_self", "gene_edges", type_="check")

    op.add_column(
        "genes",
        sa.Column("name", sa.String(length=120), nullable=False, server_default=""),
    )
    op.execute("UPDATE genes SET name = effect_type WHERE name = ''")
    op.alter_column("genes", "name", server_default=None)
    op.create_index(op.f("ix_genes_name"), "genes", ["name"], unique=False)
