from typing import Literal, cast

from app.schemas.runtime import RuntimeAgentDTO, SimulationInitDTO
from simulation_core.agents.genome import (
    ChildGenomeBuilder,
    Gene,
    GeneEdge,
    Genome,
    GenomeState,
    SimpleGenomeEffectsResolver,
    SimpleMutationModel,
    SingleCrossoverRecombinationModel,
    ThresholdGenomeUpdater,
)
from simulation_core.agents.genome.effect_type import GeneEffectType
from simulation_core.agents.registry import Agent
from simulation_core.agents.simple_softmax_policy import SimpleSoftmaxPolicy
from simulation_core.agents.state import IndividualState
from simulation_core.config import SimConfig
from simulation_core.engine.engine import SimulationEngine
from simulation_core.types import IndividualId, TerritoryId, Tick
from simulation_core.world.graph import AdjacencyListGraph
from simulation_core.world.simple_food_diffusion import SimpleFoodDiffusionModel
from simulation_core.world.territory import TerritoryState
from simulation_core.world.world_state import WorldState


class EngineFactory:
    def build_from_init_dto(self, payload: SimulationInitDTO) -> SimulationEngine:
        cfg = SimConfig(
            hunger_min=payload.config.hunger_min,
            hunger_max=payload.config.hunger_max,
            strength_min=payload.config.strength_min,
            strength_max=payload.config.strength_max,
            defense_min=payload.config.defense_min,
            defense_max=payload.config.defense_max,
            hp_min=payload.config.hp_min,
            hp_max=payload.config.hp_max,
            pregnancy_duration_ticks=payload.config.pregnancy_duration_ticks,
            beta_default=payload.config.beta_default,
        )

        world = self._build_world(payload)
        genome_updater = ThresholdGenomeUpdater()
        child_genome_builder = ChildGenomeBuilder(
            recombination_model=SingleCrossoverRecombinationModel(),
            mutation_model=SimpleMutationModel(),
        )
        genome_effects_resolver = SimpleGenomeEffectsResolver()
        food_diffusion_model = SimpleFoodDiffusionModel()

        engine = SimulationEngine(
            cfg=cfg,
            world=world,
            genome_updater=genome_updater,
            child_genome_builder=child_genome_builder,
            genome_effects_resolver=genome_effects_resolver,
            food_diffusion_model=food_diffusion_model,
            seed=0,
        )

        engine.tick = Tick(payload.tick)

        for agent_dto in payload.agents:
            agent = self._build_agent(agent_dto)
            engine.add_agent(agent)

        return engine

    def _build_world(self, payload: SimulationInitDTO) -> WorldState:
        graph = AdjacencyListGraph()

        territories: dict[TerritoryId, TerritoryState] = {}
        for territory_dto in payload.territories:
            territory_id = TerritoryId(territory_dto.id)
            territories[territory_id] = TerritoryState(
                id=territory_id,
                food=territory_dto.food,
                temperature=territory_dto.temperature,
                food_regen_per_tick=territory_dto.food_regen_per_tick,
                food_capacity=territory_dto.food_capacity,
            )
            graph.add_node(territory_id)

        for edge_dto in payload.territory_edges:
            graph.add_edge(
                TerritoryId(edge_dto.source_id),
                TerritoryId(edge_dto.target_id),
                cost=edge_dto.movement_cost,
                bidirectional=True,
            )

        return WorldState(
            territories=territories,
            _graph=graph,
        )

    def _build_agent(self, agent_dto: RuntimeAgentDTO) -> Agent:
        genome = Genome()

        for gene_dto in agent_dto.genes:
            genome.add_gene(
                Gene(
                    id=int(gene_dto.id),
                    name=gene_dto.name,
                    effect_type=GeneEffectType(gene_dto.effect_type),
                    chromosome_id=gene_dto.chromosome_id,
                    position=gene_dto.position,
                    default_active=gene_dto.default_active,
                    threshold=gene_dto.threshold,
                )
            )

        for edge_dto in agent_dto.gene_edges:
            genome.add_edge(
                GeneEdge(
                    source_gene_id=int(edge_dto.source_gene_id),
                    target_gene_id=int(edge_dto.target_gene_id),
                    weight=edge_dto.weight,
                )
            )

        genome_state = GenomeState(
            gene_activity={
                int(gene_state_dto.gene_id): gene_state_dto.is_active
                for gene_state_dto in agent_dto.gene_states
            }
        )

        state = IndividualState(
            id=IndividualId(str(agent_dto.id)),
            location=TerritoryId(agent_dto.location),
            base_strength=agent_dto.base_strength,
            base_defense=agent_dto.base_defense,
            hunger=agent_dto.hunger,
            hp=agent_dto.hp,
            sex=cast(Literal["male", "female"], agent_dto.sex),
            species_group=agent_dto.species_group,
            pregnant=agent_dto.pregnant,
            ticks_to_birth=agent_dto.ticks_to_birth,
            hunt_cooldown=agent_dto.hunt_cooldown,
            father_id=IndividualId(agent_dto.father_id)
            if agent_dto.father_id is not None
            else None,
            base_temp_pref=agent_dto.base_temp_pref,
            satisfaction=agent_dto.satisfaction,
            alive=agent_dto.alive,
        )

        return Agent(
            state=state,
            policy=SimpleSoftmaxPolicy(),
            genome=genome,
            genome_state=genome_state,
        )
