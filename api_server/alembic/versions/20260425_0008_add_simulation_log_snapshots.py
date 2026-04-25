"""add simulation log snapshots

Revision ID: 20260425_0008
Revises: 20260419_0007
Create Date: 2026-04-25 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260425_0008"
down_revision = "20260419_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "simulation_logs",
        sa.Column("snapshot", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.alter_column("simulation_logs", "snapshot", server_default=None)


def downgrade() -> None:
    op.drop_column("simulation_logs", "snapshot")
