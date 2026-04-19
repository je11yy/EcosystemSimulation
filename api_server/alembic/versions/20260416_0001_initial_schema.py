"""initial schema

Revision ID: 20260416_0001
Revises:
Create Date: 2026-04-16

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "20260416_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "agents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sex", sa.String(length=16), nullable=False),
        sa.Column("is_alive", sa.Boolean(), nullable=False),
        sa.Column("hunger", sa.Float(), nullable=False),
        sa.Column("hp", sa.Float(), nullable=False),
        sa.Column("is_pregnant", sa.Boolean(), nullable=False),
        sa.Column("ticks_to_birth", sa.Integer(), nullable=True),
        sa.Column("satisfaction", sa.Float(), nullable=False),
        sa.Column("hunt_cooldown", sa.Integer(), nullable=False),
        sa.Column("strength", sa.Float(), nullable=False),
        sa.Column("defense", sa.Float(), nullable=False),
        sa.Column("temp_pref", sa.Float(), nullable=False),
        sa.CheckConstraint("hp >= 0", name="ck_agents_hp_non_negative"),
        sa.CheckConstraint("hunger >= 0", name="ck_agents_hunger_non_negative"),
        sa.CheckConstraint("hunt_cooldown >= 0", name="ck_agents_hunt_cooldown_non_negative"),
        sa.CheckConstraint("sex IN ('male', 'female')", name="ck_agents_sex"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "genes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("effect_type", sa.String(length=64), nullable=False),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.Column("default_active", sa.Boolean(), nullable=False),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.CheckConstraint(
            "effect_type IN "
            "('hunger', 'hp', 'strength', 'defense', 'temp_pref', 'satisfaction', 'hunt_cooldown')",
            name="ck_genes_effect_type",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_genes_effect_type"), "genes", ["effect_type"], unique=False)
    op.create_index(op.f("ix_genes_name"), "genes", ["name"], unique=False)
    op.create_table(
        "genomes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_template", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_genomes_is_template"), "genomes", ["is_template"], unique=False)
    op.create_index(op.f("ix_genomes_name"), "genomes", ["name"], unique=False)
    op.create_table(
        "simulations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("tick", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'loaded', 'running', 'paused', 'stopped')",
            name="ck_simulations_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_simulations_name"), "simulations", ["name"], unique=False)
    op.create_table(
        "simulation_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.Column("tick", sa.Integer(), nullable=False),
        sa.Column("agent_decisions", sa.JSON(), nullable=False),
        sa.Column("step_result", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("simulation_id", "tick", name="uq_simulation_logs_simulation_tick"),
    )
    op.create_index(
        op.f("ix_simulation_logs_simulation_id"),
        "simulation_logs",
        ["simulation_id"],
        unique=False,
    )
    op.create_index(op.f("ix_simulation_logs_tick"), "simulation_logs", ["tick"], unique=False)
    op.create_table(
        "territories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("food", sa.Float(), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("food_regen_per_tick", sa.Float(), nullable=False),
        sa.Column("food_capacity", sa.Float(), nullable=False),
        sa.Column("x", sa.Float(), nullable=False),
        sa.Column("y", sa.Float(), nullable=False),
        sa.CheckConstraint("food >= 0", name="ck_territories_food_non_negative"),
        sa.CheckConstraint(
            "food_capacity >= 0",
            name="ck_territories_food_capacity_non_negative",
        ),
        sa.CheckConstraint(
            "food_regen_per_tick >= 0",
            name="ck_territories_food_regen_per_tick_non_negative",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nickname", sa.String(length=64), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_nickname"), "users", ["nickname"], unique=True)
    op.create_table(
        "agent_parent_relations",
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.CheckConstraint("agent_id != parent_id", name="ck_agent_parent_relations_not_self"),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("agent_id", "parent_id"),
    )
    op.create_table(
        "gene_edges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.CheckConstraint("weight >= 0", name="ck_gene_edges_weight_non_negative"),
        sa.ForeignKeyConstraint(["source_id"], ["genes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_id"], ["genes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_gene_edges_source_id"), "gene_edges", ["source_id"], unique=False)
    op.create_index(op.f("ix_gene_edges_target_id"), "gene_edges", ["target_id"], unique=False)
    op.create_table(
        "genome_agent_relations",
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("genome_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["genome_id"], ["genomes.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("agent_id", "genome_id"),
        sa.UniqueConstraint("agent_id", name="uq_genome_agent_relations_agent"),
    )
    op.create_table(
        "genome_gene_relations",
        sa.Column("genome_id", sa.Integer(), nullable=False),
        sa.Column("gene_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["gene_id"], ["genes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["genome_id"], ["genomes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("genome_id", "gene_id"),
    )
    op.create_table(
        "genome_user_relations",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("genome_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["genome_id"], ["genomes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "genome_id"),
    )
    op.create_table(
        "simulation_agent_relations",
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("agent_id", "simulation_id"),
        sa.UniqueConstraint("agent_id", name="uq_simulation_agent_relations_agent"),
    )
    op.create_table(
        "simulation_territory_relations",
        sa.Column("territory_id", sa.Integer(), nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["territory_id"], ["territories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("territory_id", "simulation_id"),
        sa.UniqueConstraint("territory_id", name="uq_simulation_territory_relations_territory"),
    )
    op.create_table(
        "simulation_user_relations",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("simulation_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["simulation_id"], ["simulations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "simulation_id"),
    )
    op.create_table(
        "territory_agent_relations",
        sa.Column("agent_id", sa.Integer(), nullable=False),
        sa.Column("territory_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["territory_id"], ["territories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("agent_id", "territory_id"),
        sa.UniqueConstraint("agent_id", name="uq_territory_agent_relations_agent"),
    )
    op.create_table(
        "territory_edges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("movement_cost", sa.Float(), nullable=False),
        sa.CheckConstraint(
            "movement_cost >= 0",
            name="ck_territory_edges_movement_cost_non_negative",
        ),
        sa.ForeignKeyConstraint(["source_id"], ["territories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_id"], ["territories.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_territory_edges_source_id"),
        "territory_edges",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_territory_edges_target_id"),
        "territory_edges",
        ["target_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_territory_edges_target_id"), table_name="territory_edges")
    op.drop_index(op.f("ix_territory_edges_source_id"), table_name="territory_edges")
    op.drop_table("territory_edges")
    op.drop_table("territory_agent_relations")
    op.drop_table("simulation_user_relations")
    op.drop_table("simulation_territory_relations")
    op.drop_table("simulation_agent_relations")
    op.drop_table("genome_user_relations")
    op.drop_table("genome_gene_relations")
    op.drop_table("genome_agent_relations")
    op.drop_index(op.f("ix_gene_edges_target_id"), table_name="gene_edges")
    op.drop_index(op.f("ix_gene_edges_source_id"), table_name="gene_edges")
    op.drop_table("gene_edges")
    op.drop_table("agent_parent_relations")
    op.drop_index(op.f("ix_users_nickname"), table_name="users")
    op.drop_table("users")
    op.drop_table("territories")
    op.drop_index(op.f("ix_simulation_logs_tick"), table_name="simulation_logs")
    op.drop_index(op.f("ix_simulation_logs_simulation_id"), table_name="simulation_logs")
    op.drop_table("simulation_logs")
    op.drop_index(op.f("ix_simulations_name"), table_name="simulations")
    op.drop_table("simulations")
    op.drop_index(op.f("ix_genomes_name"), table_name="genomes")
    op.drop_index(op.f("ix_genomes_is_template"), table_name="genomes")
    op.drop_table("genomes")
    op.drop_index(op.f("ix_genes_name"), table_name="genes")
    op.drop_index(op.f("ix_genes_effect_type"), table_name="genes")
    op.drop_table("genes")
    op.drop_table("agents")
