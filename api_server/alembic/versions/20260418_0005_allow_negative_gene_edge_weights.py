"""allow negative gene edge weights

Revision ID: 20260418_0005
Revises: 20260418_0004
Create Date: 2026-04-18

"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260418_0005"
down_revision: Union[str, None] = "20260418_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_gene_edges_weight_non_negative",
        "gene_edges",
        type_="check",
    )


def downgrade() -> None:
    op.create_check_constraint(
        "ck_gene_edges_weight_non_negative",
        "gene_edges",
        "weight >= 0",
    )
