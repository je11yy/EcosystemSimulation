"""remove persisted gene is_active

Revision ID: 20260418_0004
Revises: 20260418_0003
Create Date: 2026-04-18

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260418_0004"
down_revision: Union[str, None] = "20260418_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("genes")}
    if "is_active" in columns:
        op.drop_column("genes", "is_active")


def downgrade() -> None:
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("genes")}
    if "is_active" not in columns:
        op.add_column(
            "genes",
            sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        )
        op.alter_column("genes", "is_active", server_default=None)
