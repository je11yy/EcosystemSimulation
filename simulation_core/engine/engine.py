import random
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Literal, Optional

from simulation_core.agents.actions import ActionOption, ActionType
from simulation_core.agents.genome import GenomeContext, GenomeUpdater
from simulation_core.agents.genome.child_builder import ChildGenomeBuilder
from simulation_core.agents.genome.edge import GeneEdge
from simulation_core.agents.genome.effect_type import GeneEffectType
from simulation_core.agents.genome.effects import GenomeEffectsResolver
from simulation_core.agents.genome.gene import Gene
from simulation_core.agents.genome.genome import Genome
from simulation_core.agents.observation import Observation, ObservedIndividual, ObservedTerritory
from simulation_core.agents.phenotype import PhenotypeSnapshot
from simulation_core.agents.registry import Agent, AgentRegistry
from simulation_core.agents.state import IndividualState
from simulation_core.commands import (
    Command,
    SetTerritoryFoodCommand,
    SetTerritoryTemperatureCommand,
    StepCommand,
)
from simulation_core.config import SimConfig
from simulation_core.dto import (
    AgentDTO,
    AgentGeneDTO,
    AgentGeneEdgeDTO,
    AgentGeneStateDTO,
    SimulationStateDTO,
    TerritoryDTO,
)
from simulation_core.engine.applier import ActionApplier, AppliedActionResult
from simulation_core.engine.conflict_resolver import ConflictResolver
from simulation_core.types import IndividualId, TerritoryId, Tick
from simulation_core.world.api import WorldReadAPI
from simulation_core.world.simple_food_diffusion import SimpleFoodDiffusionModel


@dataclass(frozen=True)
class Decision:
    """Решение агента на данном тике симуляции."""

    tick: Tick
    agent_id: str
    chosen: ActionOption


@dataclass(frozen=True)
class DeathResult:
    """Результат смерти агента."""

    agent_id: str
    reason: str
    tick: Tick


@dataclass(frozen=True)
class BirthResult:
    """Результат рождения нового агента."""

    parent_id: str
    child_id: str
    tick: Tick


@dataclass(frozen=True)
class FightEvent:
    territory_id: str
    winner_id: str
    loser_id: str
    loser_hp_loss: int


@dataclass(frozen=True)
class HuntEvent:
    territory_id: str
    hunter_id: str
    target_id: str
    success: bool
    damage_to_target: int
    damage_to_hunter: int
    target_died: bool
    hunter_died: bool
    hunger_restored: int


@dataclass(frozen=True)
class StepMetrics:
    alive_population: int
    population_by_species_group: dict[str, int]
    avg_hunger_alive: float
    avg_hp_alive: float
    avg_hunt_cooldown_alive: float
    occupancy_by_territory: dict[str, int]
    action_counts: dict[str, int]
    successful_hunts: int
    births_count: int
    deaths_count: int
    deaths_by_reason: dict[str, int]


@dataclass(frozen=True)
class MetricsHistoryPoint:
    tick: int
    alive_population: int
    avg_hunger_alive: float
    avg_hp_alive: float
    avg_hunt_cooldown_alive: float
    successful_hunts: int
    births_count: int
    deaths_count: int
    population_by_species_group: dict[str, int]
    occupancy_by_territory: dict[str, int]
    action_counts: dict[str, int]
    deaths_by_reason: dict[str, int]


@dataclass(frozen=True)
class StepResult:
    """Результат одного шага симуляции."""

    tick: Tick
    decisions: list[Decision]
    applied_results: list[AppliedActionResult]
    deaths: list[DeathResult]
    births: list[BirthResult]
    fights: list[FightEvent]
    hunts: list[HuntEvent]
    metrics: StepMetrics
    metrics_history: list[MetricsHistoryPoint]


@dataclass(frozen=True)
class CommandResult:
    """Результат выполнения команды."""

    success: bool
    command_type: str
    reason: Optional[str] = None
    step_result: Optional[StepResult] = None


class SimulationEngine:
    """Основной движок симуляции экосистемы.

    Управляет всем процессом симуляции: агентами, миром, геномами,
    применением действий и обработкой команд.
    """

    def __init__(
        self,
        cfg: SimConfig,
        world: WorldReadAPI,
        genome_updater: GenomeUpdater,
        child_genome_builder: ChildGenomeBuilder,
        genome_effects_resolver: GenomeEffectsResolver,
        food_diffusion_model: SimpleFoodDiffusionModel,
        seed: int = 0,
    ) -> None:
        self.cfg = cfg
        self.world = world
        self.genome_updater = genome_updater
        self.child_genome_builder = child_genome_builder
        self.genome_effects_resolver = genome_effects_resolver
        self.rng = random.Random(seed)
        self.tick: Tick = Tick(0)
        self.agents = AgentRegistry()
        self.applier = ActionApplier()
        self.conflict_resolver = ConflictResolver()
        self.food_diffusion_model = food_diffusion_model
        self.metrics_history: list[MetricsHistoryPoint] = []

    def add_agent(self, agent: Agent) -> None:
        agent.state.validate(self.cfg)
        self.agents.add(agent)

    def build_observation(self, agent: Agent) -> Observation:
        current_id = agent.state.location

        individuals_here = []
        for other in self.agents.all():
            if other.state.location != current_id or other.state.id == agent.state.id:
                continue

            phenotype = self.build_phenotype(other)

            individuals_here.append(
                ObservedIndividual(
                    id=other.state.id,
                    sex=other.state.sex,
                    species_group=other.state.species_group,
                    hunger=other.state.hunger,
                    alive=other.state.alive,
                    effective_strength=phenotype.strength,
                    effective_defense=phenotype.defense,
                    effective_temp_pref=phenotype.temp_pref,
                )
            )

        occupant_count_by_territory: dict[TerritoryId, int] = {}
        for other in self.agents.all():
            if not other.state.alive:
                continue
            occupant_count_by_territory[other.state.location] = (
                occupant_count_by_territory.get(other.state.location, 0) + 1
            )

        neighbor_territories = []
        for edge in self.world.graph().neighbors(current_id):
            territory = self.world.get_territory(edge.to)
            neighbor_territories.append(
                ObservedTerritory(
                    id=territory.id,
                    food=territory.food,
                    food_capacity=territory.food_capacity,
                    temperature=territory.temperature,
                    movement_cost=edge.cost,
                    occupant_count=occupant_count_by_territory.get(territory.id, 0),
                )
            )

        return Observation(
            current_id=current_id,
            individuals_here=individuals_here,
            neighbor_territories=neighbor_territories,
        )

    def update_agent_genome(self, agent: Agent) -> None:
        context = GenomeContext(
            territory_id=agent.state.location,
        )

        agent.genome_state = self.genome_updater.next_state(
            genome=agent.genome,
            current_state=agent.genome_state,
            context=context,
            world=self.world,
        )

    def apply_hunger_accounting(
        self,
        applied_results: list[AppliedActionResult],
    ) -> None:
        result_by_agent_id = {result.agent_id: result for result in applied_results}

        for agent in self.agents.all():
            if not agent.state.alive:
                continue

            basal_cost = 1
            action_cost_or_gain = 0
            pregnancy_cost = 1 if agent.state.pregnant else 0

            result = result_by_agent_id.get(str(agent.state.id))
            if result is not None:
                action_cost_or_gain = result.hunger_delta

            net_delta = basal_cost + action_cost_or_gain + pregnancy_cost

            if net_delta > 0:
                agent.state.increase_hunger(net_delta, self.cfg)
            elif net_delta < 0:
                agent.state.decrease_hunger(-net_delta, self.cfg)

    def regenerate_territories(self) -> None:
        for territory in self.world.all_territories():
            territory.regenerate_food()
        self.food_diffusion_model.diffuse(self.world)

    def build_territory_dtos(self) -> list[TerritoryDTO]:
        territories: list[TerritoryDTO] = []

        for territory in self.world.all_territories():
            territories.append(
                TerritoryDTO(
                    id=territory.id,
                    food=territory.food,
                    temperature=territory.temperature,
                    food_regen_per_tick=territory.food_regen_per_tick,
                    food_capacity=territory.food_capacity,
                )
            )

        return territories

    def build_agent_dtos(self) -> list[AgentDTO]:
        agents: list[AgentDTO] = []

        for agent in self.agents.all():
            active_genes = [
                gene_id
                for gene_id, is_active in agent.genome_state.gene_activity.items()
                if is_active
            ]

            effective_strength = self.get_effective_strength(agent)
            effective_defense = self.get_effective_defense(agent)
            effective_temp_pref = self.get_effective_temp_pref(agent)

            genes = [
                AgentGeneDTO(
                    id=gene.id,
                    name=gene.name,
                    effect_type=gene.effect_type,
                    chromosome_id=gene.chromosome_id,
                    position=gene.position,
                    default_active=gene.default_active,
                    threshold=gene.threshold,
                )
                for gene in agent.genome.all_genes()
            ]

            gene_edges = [
                AgentGeneEdgeDTO(
                    source_gene_id=str(edge.source_gene_id),
                    target_gene_id=str(edge.target_gene_id),
                    weight=edge.weight,
                )
                for edge in agent.genome.edges
            ]

            gene_states = [
                AgentGeneStateDTO(
                    gene_id=gene_id,
                    is_active=is_active,
                )
                for gene_id, is_active in agent.genome_state.gene_activity.items()
            ]

            agents.append(
                AgentDTO(
                    id=str(agent.state.id),
                    location=str(agent.state.location),
                    hunger=agent.state.hunger,
                    hp=agent.state.hp,
                    base_strength=agent.state.base_strength,
                    effective_strength=effective_strength,
                    base_defense=agent.state.base_defense,
                    hunt_cooldown=agent.state.hunt_cooldown,
                    effective_defense=effective_defense,
                    sex=agent.state.sex,
                    species_group=(
                        agent.state.species_group
                        if hasattr(agent.state, "species_group")
                        else "default"
                    ),
                    pregnant=agent.state.pregnant,
                    ticks_to_birth=agent.state.ticks_to_birth,
                    father_id=(
                        str(agent.state.father_id) if agent.state.father_id is not None else None
                    ),
                    base_temp_pref=agent.state.base_temp_pref,
                    effective_temp_pref=effective_temp_pref,
                    satisfaction=agent.state.satisfaction,
                    alive=agent.state.alive,
                    active_genes=active_genes,
                    genes=genes,
                    gene_edges=gene_edges,
                    gene_states=gene_states,
                )
            )

        return agents

    def get_state(self) -> SimulationStateDTO:
        return SimulationStateDTO(
            tick=int(self.tick),
            territories=self.build_territory_dtos(),
            agents=self.build_agent_dtos(),
        )

    def step(self) -> StepResult:
        decisions: List[Decision] = []
        applied_results: List[AppliedActionResult] = []
        fights: list[FightEvent] = []
        hunts: list[HuntEvent] = []

        decisions_buffer: list[tuple[Agent, ActionOption, PhenotypeSnapshot]] = []

        for agent in self.agents.all():
            if not agent.state.alive:
                continue

            self.update_agent_genome(agent)
            obs = self.build_observation(agent)
            phenotype = self.build_phenotype(agent)

            chosen = agent.policy.decide(
                state=agent.state,
                phenotype=phenotype,
                genome=agent.genome,
                genome_state=agent.genome_state,
                obs=obs,
                world=self.world,
                rng=self.rng,
                cfg=self.cfg,
            )

            decisions.append(
                Decision(
                    tick=self.tick,
                    agent_id=str(agent.state.id),
                    chosen=chosen,
                )
            )
            decisions_buffer.append((agent, chosen, phenotype))

        eat_claims_by_territory: dict[str, list[tuple[Agent, PhenotypeSnapshot]]] = defaultdict(
            list
        )

        for agent, action, phenotype in decisions_buffer:
            if not agent.state.alive:
                applied_results.append(
                    AppliedActionResult(
                        agent_id=str(agent.state.id),
                        action_type=action.type.value,
                        success=False,
                        reason="Agent died before action resolution",
                    )
                )
                continue

            if action.type == ActionType.EAT:
                eat_claims_by_territory[str(agent.state.location)].append((agent, phenotype))
                continue

            result = self.applier.apply(
                agent=agent,
                action=action,
                world=self.world,
                agents=self.agents,
                cfg=self.cfg,
                rng=self.rng,
                actor_phenotype=phenotype,
                phenotype_provider=self.build_phenotype,
            )
            applied_results.append(result)

            if action.type == ActionType.HUNT and action.target_id is not None:
                target_id = result.target_id or (
                    str(action.target_id) if action.target_id is not None else "unknown"
                )

                hunts.append(
                    HuntEvent(
                        territory_id=str(agent.state.location),
                        hunter_id=str(agent.state.id),
                        target_id=target_id,
                        success=result.success,
                        damage_to_target=result.damage_to_target,
                        damage_to_hunter=result.hp_loss,
                        target_died=result.target_died,
                        hunter_died=result.hunter_died,
                        hunger_restored=result.hunger_restored,
                    )
                )

        for territory_id, contenders in eat_claims_by_territory.items():
            alive_contenders = [
                (agent, phenotype) for agent, phenotype in contenders if agent.state.alive
            ]

            if not alive_contenders:
                continue

            territory = self.world.get_territory(TerritoryId(territory_id))
            available_food_units = int(territory.food)

            if available_food_units <= 0:
                for agent, _phenotype in alive_contenders:
                    applied_results.append(
                        AppliedActionResult(
                            agent_id=str(agent.state.id),
                            action_type=ActionType.EAT.value,
                            success=False,
                            reason="No food available on territory",
                            consumed_food=False,
                        )
                    )
                continue

            if available_food_units >= len(alive_contenders):
                for agent, _phenotype in alive_contenders:
                    result = self.applier.apply_successful_eat(
                        agent=agent,
                        world=self.world,
                        cfg=self.cfg,
                    )
                    applied_results.append(result)
                continue

            winner, fight_results = self.conflict_resolver.resolve_food_conflict(
                territory_id=territory_id,
                contenders=alive_contenders,
                rng=self.rng,
                cfg=self.cfg,
            )

            for fr in fight_results:
                fights.append(
                    FightEvent(
                        territory_id=fr.territory_id,
                        winner_id=fr.winner_id,
                        loser_id=fr.loser_id,
                        loser_hp_loss=fr.loser_hp_loss,
                    )
                )
                applied_results.append(
                    AppliedActionResult(
                        agent_id=fr.loser_id,
                        action_type="fight_loss",
                        success=True,
                        hp_loss=fr.loser_hp_loss,
                    )
                )

            eat_result = self.applier.apply_successful_eat(
                agent=winner,
                world=self.world,
                cfg=self.cfg,
            )
            applied_results.append(eat_result)

        combat_deaths = self.resolve_hp_deaths()

        self.apply_hunger_accounting(applied_results)
        self.regenerate_territories()

        births = self.resolve_births()
        starvation_deaths = self.apply_starvation_damage()
        self.decay_hunt_cooldowns()

        deaths = combat_deaths + starvation_deaths

        metrics = self._collect_step_metrics(
            decisions=decisions,
            applied_results=applied_results,
            deaths=deaths,
            births=births,
            hunts=hunts,
        )

        history_point = self._make_metrics_history_point(
            tick=self.tick,
            metrics=metrics,
        )
        self.metrics_history.append(history_point)

        result = StepResult(
            tick=self.tick,
            decisions=decisions,
            applied_results=applied_results,
            deaths=deaths,
            births=births,
            fights=fights,
            hunts=hunts,
            metrics=metrics,
            metrics_history=list(self.metrics_history),
        )

        self.tick = Tick(int(self.tick) + 1)
        return result

    def handle_command(self, command: Command) -> CommandResult:
        if isinstance(command, StepCommand):
            last_result: Optional[StepResult] = None
            for _ in range(command.steps):
                last_result = self.step()

            return CommandResult(
                success=True,
                command_type="StepCommand",
                step_result=last_result,
            )

        if isinstance(command, SetTerritoryFoodCommand):
            territory = self.world.get_territory(command.territory_id)
            territory.food = command.food
            return CommandResult(
                success=True,
                command_type="SetTerritoryFoodCommand",
            )

        if isinstance(command, SetTerritoryTemperatureCommand):
            territory = self.world.get_territory(command.territory_id)
            territory.temperature = command.temperature
            return CommandResult(
                success=True,
                command_type="SetTerritoryTemperatureCommand",
            )

        return CommandResult(
            success=False,
            command_type=type(command).__name__,
            reason="Unsupported command",
        )

    def handle_commands(self, commands: list[Command]) -> list[CommandResult]:
        results: list[CommandResult] = []
        for command in commands:
            results.append(self.handle_command(command))
        return results

    def _generate_child_id(self) -> IndividualId:
        return IndividualId(f"child_{int(self.tick)}_{self.rng.randint(1000, 9999)}")

    def resolve_births(self) -> list[BirthResult]:
        births: list[BirthResult] = []
        new_agents: list[Agent] = []

        for mother in self.agents.all():
            if not mother.state.pregnant:
                continue

            mother.state.ticks_to_birth -= 1

            if mother.state.ticks_to_birth > 0:
                continue

            father_id = mother.state.father_id
            if father_id is None:
                mother.state.pregnant = False
                mother.state.ticks_to_birth = 0
                continue

            try:
                father = self.agents.get(father_id)
            except KeyError:
                mother.state.pregnant = False
                mother.state.ticks_to_birth = 0
                mother.state.father_id = None
                continue

            child_id = self._generate_child_id()
            child_sex: Literal["male", "female"] = self.rng.choice(["male", "female"])

            child_genome = self.child_genome_builder.build_child_genome(
                parent_a=mother,
                parent_b=father,
                rng=self.rng,
            )
            child_genome_state = child_genome.build_default_state()

            child_strength = max(
                self.cfg.strength_min,
                min(
                    self.cfg.strength_max,
                    round((mother.state.base_strength + father.state.base_strength) / 2),
                ),
            )
            child_defense = max(
                self.cfg.defense_min,
                min(
                    self.cfg.defense_max,
                    round((mother.state.base_defense + father.state.base_defense) / 2),
                ),
            )
            child_temp_pref = (mother.state.base_temp_pref + father.state.base_temp_pref) / 2.0

            child_state = IndividualState(
                id=child_id,
                location=mother.state.location,
                hunger=0,
                hp=self.cfg.hp_max,
                base_strength=child_strength,
                base_defense=child_defense,
                sex=child_sex,
                species_group=mother.state.species_group,
                base_temp_pref=child_temp_pref,
                hunt_cooldown=0,
            )

            child_agent = Agent(
                state=child_state,
                policy=type(mother.policy)(),
                genome=child_genome,
                genome_state=child_genome_state,
            )

            new_agents.append(child_agent)

            mother.state.pregnant = False
            mother.state.ticks_to_birth = 0
            mother.state.father_id = None

            births.append(
                BirthResult(
                    parent_id=str(mother.state.id),
                    child_id=str(child_id),
                    tick=self.tick,
                )
            )

        for child_agent in new_agents:
            self.add_agent(child_agent)

        return births

    def create_default_genome(self) -> Genome:
        genome = Genome()

        genome.add_gene(
            Gene(
                id=1,
                name="Hunger drive",
                effect_type=GeneEffectType.HUNGER_DRIVE,
                chromosome_id="chr1",
                position=1.0,
                threshold=0.2,
            )
        )
        genome.add_gene(
            Gene(
                id=2,
                name="Risk movement",
                effect_type=GeneEffectType.RISK_MOVE,
                chromosome_id="chr1",
                position=2.0,
                threshold=0.0,
            )
        )
        genome.add_gene(
            Gene(
                id=3,
                name="Low activity",
                effect_type=GeneEffectType.LOW_ACTIVITY,
                chromosome_id="chr1",
                position=3.0,
                threshold=0.3,
            )
        )
        genome.add_gene(
            Gene(
                id=4,
                name="Heat resistance",
                effect_type=GeneEffectType.HEAT_RESISTANCE,
                chromosome_id="chr2",
                position=1.0,
                threshold=0.0,
            )
        )
        genome.add_gene(
            Gene(
                id=5,
                name="Cold resistance",
                effect_type=GeneEffectType.COLD_RESISTANCE,
                chromosome_id="chr2",
                position=2.0,
                threshold=0.0,
            )
        )
        genome.add_gene(
            Gene(
                id=6,
                name="Reproduction drive",
                effect_type=GeneEffectType.REPRODUCTION_DRIVE,
                chromosome_id="chr2",
                position=3.0,
                threshold=0.1,
            )
        )

        genome.add_edge(
            GeneEdge(
                source_gene_id=1,
                target_gene_id=2,
                weight=0.4,
            )
        )

        return genome

    def get_effective_strength(self, agent: Agent) -> int:
        effects = self.genome_effects_resolver.resolve(
            genome=agent.genome,
            genome_state=agent.genome_state,
        )
        return max(
            self.cfg.strength_min,
            min(self.cfg.strength_max, agent.state.base_strength + effects.strength_delta),
        )

    def get_effective_defense(self, agent: Agent) -> int:
        effects = self.genome_effects_resolver.resolve(
            genome=agent.genome,
            genome_state=agent.genome_state,
        )
        return max(
            self.cfg.defense_min,
            min(self.cfg.defense_max, agent.state.base_defense + effects.defense_delta),
        )

    def get_effective_temp_pref(self, agent: Agent) -> float:
        effects = self.genome_effects_resolver.resolve(
            genome=agent.genome,
            genome_state=agent.genome_state,
        )
        return agent.state.base_temp_pref + effects.temp_pref_delta

    def build_phenotype(self, agent: Agent) -> PhenotypeSnapshot:
        return PhenotypeSnapshot(
            strength=self.get_effective_strength(agent),
            defense=self.get_effective_defense(agent),
            temp_pref=self.get_effective_temp_pref(agent),
        )

    def resolve_hp_deaths(self) -> list[DeathResult]:
        deaths: list[DeathResult] = []
        to_remove: list[IndividualId] = []

        for agent in self.agents.all():
            if not agent.state.alive or agent.state.hp <= self.cfg.hp_min:
                agent.state.alive = False
                deaths.append(
                    DeathResult(
                        agent_id=str(agent.state.id),
                        reason="combat",
                        tick=self.tick,
                    )
                )
                to_remove.append(agent.state.id)

        for agent_id in to_remove:
            if any(str(a.state.id) == str(agent_id) for a in self.agents.all()):
                self.agents.remove(agent_id)

        return deaths

    def apply_starvation_damage(self) -> list[DeathResult]:
        deaths: list[DeathResult] = []
        to_remove: list[IndividualId] = []

        for agent in self.agents.all():
            if not agent.state.alive:
                continue

            if agent.state.hunger < self.cfg.hunger_max:
                continue

            hp_before = agent.state.hp
            agent.state.decrease_hp(1, self.cfg)

            if hp_before > self.cfg.hp_min and agent.state.hp <= self.cfg.hp_min:
                agent.state.alive = False
                deaths.append(
                    DeathResult(
                        agent_id=str(agent.state.id),
                        reason="starvation",
                        tick=self.tick,
                    )
                )
                to_remove.append(agent.state.id)

        for agent_id in to_remove:
            if any(str(a.state.id) == str(agent_id) for a in self.agents.all()):
                self.agents.remove(agent_id)

        return deaths

    def decay_hunt_cooldowns(self) -> None:
        for agent in self.agents.all():
            if not agent.state.alive:
                continue

            if agent.state.hunt_cooldown > 0:
                agent.state.hunt_cooldown -= 1

    def _collect_step_metrics(
        self,
        decisions: list[Decision],
        applied_results: list[AppliedActionResult],
        deaths: list[DeathResult],
        births: list[BirthResult],
        hunts: list[HuntEvent],
    ) -> StepMetrics:
        alive_agents = [agent for agent in self.agents.all() if agent.state.alive]

        population_by_species_group: dict[str, int] = {}
        for agent in alive_agents:
            species_group = agent.state.species_group
            population_by_species_group[species_group] = (
                population_by_species_group.get(species_group, 0) + 1
            )

        occupancy_by_territory: dict[str, int] = {}
        for agent in alive_agents:
            territory_id = str(agent.state.location)
            occupancy_by_territory[territory_id] = occupancy_by_territory.get(territory_id, 0) + 1

        action_counts: dict[str, int] = {}
        for decision in decisions:
            action_type = decision.chosen.type.value
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        deaths_by_reason: dict[str, int] = {}
        for death in deaths:
            deaths_by_reason[death.reason] = deaths_by_reason.get(death.reason, 0) + 1

        alive_population = len(alive_agents)

        avg_hunger_alive = (
            sum(agent.state.hunger for agent in alive_agents) / alive_population
            if alive_population > 0
            else 0.0
        )
        avg_hp_alive = (
            sum(agent.state.hp for agent in alive_agents) / alive_population
            if alive_population > 0
            else 0.0
        )
        avg_hunt_cooldown_alive = (
            sum(agent.state.hunt_cooldown for agent in alive_agents) / alive_population
            if alive_population > 0
            else 0.0
        )

        successful_hunts = sum(1 for hunt in hunts if hunt.success)

        return StepMetrics(
            alive_population=alive_population,
            population_by_species_group=population_by_species_group,
            avg_hunger_alive=avg_hunger_alive,
            avg_hp_alive=avg_hp_alive,
            avg_hunt_cooldown_alive=avg_hunt_cooldown_alive,
            occupancy_by_territory=occupancy_by_territory,
            action_counts=action_counts,
            successful_hunts=successful_hunts,
            births_count=len(births),
            deaths_count=len(deaths),
            deaths_by_reason=deaths_by_reason,
        )

    def _make_metrics_history_point(
        self,
        tick: Tick,
        metrics: StepMetrics,
    ) -> MetricsHistoryPoint:
        return MetricsHistoryPoint(
            tick=int(tick),
            alive_population=metrics.alive_population,
            avg_hunger_alive=metrics.avg_hunger_alive,
            avg_hp_alive=metrics.avg_hp_alive,
            avg_hunt_cooldown_alive=metrics.avg_hunt_cooldown_alive,
            successful_hunts=metrics.successful_hunts,
            births_count=metrics.births_count,
            deaths_count=metrics.deaths_count,
            population_by_species_group=dict(metrics.population_by_species_group),
            occupancy_by_territory=dict(metrics.occupancy_by_territory),
            action_counts=dict(metrics.action_counts),
            deaths_by_reason=dict(metrics.deaths_by_reason),
        )
