"""update gene effect types

Revision ID: 20260418_0002
Revises: 20260416_0001
Create Date: 2026-04-18

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260418_0002"
down_revision: Union[str, None] = "20260416_0001"
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
)

OLD_EFFECT_TYPES = (
    "hunger",
    "hp",
    "strength",
    "defense",
    "temp_pref",
    "satisfaction",
    "hunt_cooldown",
)


def _check_constraint(values: tuple[str, ...]) -> str:
    quoted_values = ", ".join(f"'{value}'" for value in values)
    return f"effect_type IN ({quoted_values})"


def upgrade() -> None:
    op.drop_constraint("ck_genes_effect_type", "genes", type_="check")
    op.execute(
        sa.text(
            """
            UPDATE genes
            SET effect_type = CASE effect_type
                WHEN 'hp' THEN 'MAX_HP'
                WHEN 'strength' THEN 'STRENGTH'
                WHEN 'defense' THEN 'DEFENSE'
                WHEN 'hunger' THEN 'HUNGER_DRIVE'
                WHEN 'temp_pref' THEN 'HEAT_RESISTANCE'
                WHEN 'satisfaction' THEN 'SOCIAL_TOLERANCE'
                WHEN 'hunt_cooldown' THEN 'PREDATION_DRIVE'
                ELSE effect_type
            END
            """
        )
    )
    op.create_check_constraint(
        "ck_genes_effect_type",
        "genes",
        _check_constraint(NEW_EFFECT_TYPES),
    )


def downgrade() -> None:
    op.drop_constraint("ck_genes_effect_type", "genes", type_="check")
    op.execute(
        sa.text(
            """
            UPDATE genes
            SET effect_type = CASE effect_type
                WHEN 'MAX_HP' THEN 'hp'
                WHEN 'STRENGTH' THEN 'strength'
                WHEN 'DEFENSE' THEN 'defense'
                WHEN 'HUNGER_DRIVE' THEN 'hunger'
                WHEN 'HEAT_RESISTANCE' THEN 'temp_pref'
                WHEN 'COLD_RESISTANCE' THEN 'temp_pref'
                WHEN 'SOCIAL_TOLERANCE' THEN 'satisfaction'
                WHEN 'PREDATION_DRIVE' THEN 'hunt_cooldown'
                ELSE 'hunger'
            END
            """
        )
    )
    op.create_check_constraint(
        "ck_genes_effect_type",
        "genes",
        _check_constraint(OLD_EFFECT_TYPES),
    )
