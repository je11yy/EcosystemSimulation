from app.schemas.simulation.init import BuildSimulationRequest, RuntimeGenome
from simulation_core import SimConfig
from simulation_core.agent.state import AgentState
from simulation_core.engine import Engine
from simulation_core.enums import AgentSex
from simulation_core.genome import Gene, GeneEffectType, Genome
from simulation_core.world import TerritoryState


class EngineFactory:
    def build(self, payload: BuildSimulationRequest) -> Engine:
        engine = Engine(cfg=self._build_config(payload))
        engine.tick = payload.tick

        for territory in payload.territories:
            engine.world.add_territory(
                TerritoryState(
                    id=territory.id,
                    food=territory.food,
                    temperature=territory.temperature,
                    food_regen_per_tick=territory.food_regen_per_tick,
                    food_capacity=territory.food_capacity,
                )
            )

        for edge in payload.territory_edges:
            engine.world.add_edge(edge.source, edge.target, edge.weight)

        genomes_by_id = {
            genome_payload.id: self._build_genome(genome_payload)
            for genome_payload in payload.genomes
        }

        for agent in payload.agents:
            genome = genomes_by_id.get(agent.genome_id)
            if genome is None:
                genome = Genome()

            state = AgentState(
                id=agent.id,
                sex=AgentSex(agent.sex),
                hunger=agent.hunger,
                hp=agent.hp,
                is_pregnant=agent.pregnant,
                ticks_to_birth=agent.ticks_to_birth,
                satisfaction=agent.satisfaction,
                hunt_cooldown=agent.hunt_cooldown,
                base_strength=agent.strength,
                base_defense=agent.defense,
                base_temp_pref=agent.temp_pref,
                location=agent.territory_id,
                is_alive=agent.is_alive,
            )
            engine.add_agent(state, genome)

        return engine

    def _build_config(self, payload: BuildSimulationRequest) -> SimConfig:
        return SimConfig(**payload.config.model_dump())

    def _build_genome(self, payload: RuntimeGenome) -> Genome:
        genome = Genome()
        for gene in payload.genes:
            genome.add_gene(
                Gene(
                    id=gene.id,
                    name=gene.name,
                    effect_type=GeneEffectType(gene.effect_type),
                    threshold=gene.threshold,
                    weight=gene.weight,
                    default_active=gene.default_active,
                    is_active=False,
                )
            )

        for edge in payload.edges:
            if edge.source not in genome.genes or edge.target not in genome.genes:
                continue
            genome.add_edge(edge.source, edge.target, edge.weight)

        return genome
