from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.agent import Agent
from app.models.gene import Gene
from app.models.gene_edge import GeneEdge
from app.models.gene_state import GeneState
from app.models.simulation import Simulation
from app.models.territory import Territory
from app.models.territory_edge import TerritoryEdge
from app.models.user import User

router = APIRouter(prefix="/debug", tags=["debug"])


@router.post("/seed-simulation")
async def seed_simulation(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: int = 1,
) -> dict[str, Any]:
    # создаём тестового пользователя если не существует
    from sqlalchemy import select

    existing_user = await db.execute(select(User).where(User.id == user_id))
    if existing_user.scalar_one_or_none() is None:
        user = User(
            id=user_id,
            email=f"test{user_id}@example.com",
            hashed_password="hashed_test_password",
        )
        db.add(user)
        await db.flush()

    simulation = Simulation(
        user_id=user_id,
        name="Test simulation",
        status="draft",
        tick=0,
    )
    db.add(simulation)
    await db.flush()

    t1 = Territory(
        simulation_id=simulation.id,
        food=6.0,
        temperature=20.0,
        food_regen_per_tick=0.5,
        food_capacity=10.0,
        x=0,
        y=0,
    )
    t2 = Territory(
        simulation_id=simulation.id,
        food=2.0,
        temperature=24.0,
        food_regen_per_tick=0.3,
        food_capacity=8.0,
        x=1,
        y=0,
    )
    t3 = Territory(
        simulation_id=simulation.id,
        food=4.0,
        temperature=17.0,
        food_regen_per_tick=0.4,
        food_capacity=9.0,
        x=0,
        y=1,
    )
    db.add_all([t1, t2, t3])
    await db.flush()

    db.add_all(
        [
            TerritoryEdge(
                simulation_id=simulation.id,
                source_territory_id=t1.id,
                target_territory_id=t2.id,
                movement_cost=1.0,
            ),
            TerritoryEdge(
                simulation_id=simulation.id,
                source_territory_id=t1.id,
                target_territory_id=t3.id,
                movement_cost=1.0,
            ),
        ]
    )

    a1 = Agent(
        simulation_id=simulation.id,
        territory_id=t1.id,
        hunger=3,
        hp=5,
        base_strength=3,
        base_defense=2,
        sex="female",
        pregnant=False,
        ticks_to_birth=0,
        father_id=None,
        base_temp_pref=20.0,
        satisfaction=1.0,
        alive=True,
    )
    a2 = Agent(
        simulation_id=simulation.id,
        territory_id=t1.id,
        hunger=2,
        hp=5,
        base_strength=4,
        base_defense=3,
        sex="male",
        pregnant=False,
        ticks_to_birth=0,
        father_id=None,
        base_temp_pref=22.0,
        satisfaction=1.0,
        alive=True,
    )
    db.add_all([a1, a2])
    await db.flush()

    for agent in (a1, a2):
        db.add_all(
            [
                Gene(
                    agent_id=agent.id,
                    gene_key="g_hunger_drive",
                    name="Hunger drive",
                    chromosome_id="chr1",
                    position=1.0,
                    default_active=False,
                    threshold=0.2,
                ),
                Gene(
                    agent_id=agent.id,
                    gene_key="g_risk_move",
                    name="Risk movement",
                    chromosome_id="chr1",
                    position=2.0,
                    default_active=False,
                    threshold=0.0,
                ),
                Gene(
                    agent_id=agent.id,
                    gene_key="g_heat_resistance",
                    name="Heat resistance",
                    chromosome_id="chr2",
                    position=1.0,
                    default_active=False,
                    threshold=0.0,
                ),
            ]
        )
        db.add(
            GeneEdge(
                agent_id=agent.id,
                source_gene_key="g_hunger_drive",
                target_gene_key="g_risk_move",
                weight=0.4,
            )
        )
        db.add_all(
            [
                GeneState(
                    agent_id=agent.id,
                    gene_key="g_hunger_drive",
                    is_active=False,
                ),
                GeneState(
                    agent_id=agent.id,
                    gene_key="g_risk_move",
                    is_active=False,
                ),
                GeneState(
                    agent_id=agent.id,
                    gene_key="g_heat_resistance",
                    is_active=False,
                ),
            ]
        )

    await db.commit()

    return {
        "ok": True,
        "simulation_id": simulation.id,
    }
