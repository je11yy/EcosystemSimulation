"""restore directed territory edges

Revision ID: 20260425_0010
Revises: 20260425_0009
Create Date: 2026-04-25

"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260425_0010"
down_revision: Union[str, None] = "20260425_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_territory_edges_canonical_order", "territory_edges", type_="check")
    op.create_check_constraint(
        "ck_territory_edges_not_self",
        "territory_edges",
        "source_id != target_id",
    )
    op.execute(
        """
        INSERT INTO territory_edges (source_id, target_id, movement_cost)
        SELECT te.target_id, te.source_id, te.movement_cost
        FROM territory_edges te
        WHERE NOT EXISTS (
            SELECT 1
            FROM territory_edges reverse_te
            WHERE reverse_te.source_id = te.target_id
              AND reverse_te.target_id = te.source_id
        )
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM territory_edges te
        WHERE te.source_id > te.target_id
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
    op.drop_constraint("ck_territory_edges_not_self", "territory_edges", type_="check")
    op.create_check_constraint(
        "ck_territory_edges_canonical_order",
        "territory_edges",
        "source_id < target_id",
    )
