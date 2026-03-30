from app.models.simulation import Simulation
from app.schemas.simulation_runtime import (
    RuntimeAgentDTO,
    RuntimeConfigDTO,
    RuntimeGeneDTO,
    RuntimeGeneEdgeDTO,
    RuntimeGeneStateDTO,
    RuntimeTerritoryDTO,
    RuntimeTerritoryEdgeDTO,
    SimulationInitDTO,
)


class EngineMapper:
    def to_init_dto(self, simulation: Simulation) -> SimulationInitDTO:
        return SimulationInitDTO(
            simulation_id=str(simulation.id),
            tick=simulation.tick,
            config=RuntimeConfigDTO(),
            territories=[
                RuntimeTerritoryDTO(
                    id=str(territory.id),
                    food=territory.food,
                    temperature=territory.temperature,
                    food_regen_per_tick=territory.food_regen_per_tick,
                    food_capacity=territory.food_capacity,
                    x=territory.x,
                    y=territory.y,
                )
                for territory in simulation.territories
            ],
            territory_edges=[
                RuntimeTerritoryEdgeDTO(
                    source_id=str(edge.source_territory_id),
                    target_id=str(edge.target_territory_id),
                    movement_cost=edge.movement_cost,
                )
                for edge in simulation.territory_edges
            ],
            agents=[
                RuntimeAgentDTO(
                    id=str(agent.id),
                    location=str(agent.territory_id),
                    hunger=agent.hunger,
                    hp=agent.hp,
                    base_strength=agent.base_strength,
                    base_defense=agent.base_defense,
                    sex=agent.sex,
                    species_group=agent.species_group,
                    pregnant=agent.pregnant,
                    ticks_to_birth=agent.ticks_to_birth,
                    hunt_cooldown=agent.hunt_cooldown,
                    father_id=str(agent.father_id) if agent.father_id is not None else None,
                    base_temp_pref=agent.base_temp_pref,
                    satisfaction=agent.satisfaction,
                    alive=agent.alive,
                    genes=[
                        RuntimeGeneDTO(
                            id=str(gene.id),
                            effect_type=gene.effect_type.value,
                            name=gene.name,
                            chromosome_id=gene.chromosome_id,
                            position=gene.position,
                            default_active=gene.default_active,
                            threshold=gene.threshold,
                        )
                        for gene in agent.genes
                    ],
                    gene_edges=[
                        RuntimeGeneEdgeDTO(
                            source_gene_id=str(edge.source_gene_id),
                            target_gene_id=str(edge.target_gene_id),
                            weight=edge.weight,
                        )
                        for edge in agent.gene_edges
                    ],
                    gene_states=[
                        RuntimeGeneStateDTO(
                            gene_id=str(gene_state.gene_id),
                            is_active=gene_state.is_active,
                        )
                        for gene_state in agent.gene_states
                    ],
                )
                for agent in simulation.agents
            ],
        )
