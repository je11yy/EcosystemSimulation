"""add mutation rate gene effect

Revision ID: 20260419_0006
Revises: 20260418_0005
Create Date: 2026-04-19

"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260419_0006"
down_revision: Union[str, None] = "20260418_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_EFFECT_TYPES = (
    "MAX_HP",
    "STRENGTH",
    "DEFENSE",
    "METABOLISM",
    "HUNGER_DRIVE",
    "DISPERSAL_DRIVE",
    "SITE_FIDELITY",
    "REPRODUCTION_DRIVE",
    "HEAT_RESISTANCE",
    "COLD_RESISTANCE",
    "AGGRESSION_DRIVE",
    "PREDATION_DRIVE",
    "CARNIVORE_DIGESTION",
    "CANNIBAL_TOLERANCE",
    "SOCIAL_TOLERANCE",
    "MUTATION_RATE",
)

OLD_EFFECT_TYPES = NEW_EFFECT_TYPES[:-1]


def _check_constraint(values: tuple[str, ...]) -> str:
    quoted_values = ", ".join(f"'{value}'" for value in values)
    return f"effect_type IN ({quoted_values})"


def upgrade() -> None:
    op.drop_constraint("ck_genes_effect_type", "genes", type_="check")
    op.create_check_constraint(
        "ck_genes_effect_type",
        "genes",
        _check_constraint(NEW_EFFECT_TYPES),
    )


def downgrade() -> None:
    op.execute("UPDATE genes SET effect_type = 'METABOLISM' WHERE effect_type = 'MUTATION_RATE'")
    op.drop_constraint("ck_genes_effect_type", "genes", type_="check")
    op.create_check_constraint(
        "ck_genes_effect_type",
        "genes",
        _check_constraint(OLD_EFFECT_TYPES),
    )
