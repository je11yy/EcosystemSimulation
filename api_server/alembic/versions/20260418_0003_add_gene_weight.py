"""add gene weight

Revision ID: 20260418_0003
Revises: 20260418_0002
Create Date: 2026-04-18

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260418_0003"
down_revision: Union[str, None] = "20260418_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "genes",
        sa.Column("weight", sa.Float(), server_default="1.0", nullable=False),
    )
    op.create_check_constraint(
        "ck_genes_weight_non_negative",
        "genes",
        "weight >= 0",
    )
    op.alter_column("genes", "weight", server_default=None)


def downgrade() -> None:
    op.drop_constraint("ck_genes_weight_non_negative", "genes", type_="check")
    op.drop_column("genes", "weight")
