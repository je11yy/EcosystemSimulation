import random
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Literal, Optional

from simulation_core.agents.actions import ActionOption
from simulation_core.agents.genome import GenomeContext, GenomeUpdater
from simulation_core.agents.genome.child_builder import ChildGenomeBuilder
from simulation_core.agents.genome.edge import GeneEdge
from simulation_core.agents.genome.effects import GenomeEffectsResolver
from simulation_core.agents.genome.gene import Gene
from simulation_core.agents.genome.genome import Genome
from simulation_core.agents.observation import Observation
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
    SimulationStateDTO,
    TerritoryDTO,
)
from simulation_core.engine.applier import ActionApplier, AppliedActionResult
from simulation_core.engine.conflict_resolver import ConflictResolver
from simulation_core.types import IndividualId, Tick
from simulation_core.world.api import WorldReadAPI


@dataclass(frozen=True)
class Decision:
    """Решение агента на данном тике симуляции."""

    tick: Tick  # Номер тика, на котором было принято решение
    agent_id: str  # Идентификатор агента, принявшего решение
    chosen: ActionOption  # Выбранное действие агента


@dataclass(frozen=True)
class DeathResult:
    """Результат смерти агента."""

    agent_id: str  # Идентификатор умершего агента
    reason: str  # Причина смерти (например, "starvation" - голод)
    tick: Tick  # Тик, на котором произошла смерть


@dataclass(frozen=True)
class BirthResult:
    """Результат рождения нового агента."""

    parent_id: str  # Идентификатор родителя
    child_id: str  # Идентификатор новорожденного агента
    tick: Tick  # Тик, на котором произошло рождение


@dataclass(frozen=True)
class FightEvent:
    territory_id: str
    winner_id: str
    loser_id: str
    loser_hp_loss: int


@dataclass(frozen=True)
class StepResult:
    """Результат одного шага симуляции."""

    tick: Tick  # Номер тика
    decisions: list[Decision]  # Список решений всех агентов на этом тике
    applied_results: list[AppliedActionResult]  # Результаты применения действий
    deaths: list[DeathResult]  # Список смертей на этом тике
    births: list[BirthResult]  # Список рождений на этом тике
    fights: list[FightEvent]


@dataclass(frozen=True)
class CommandResult:
    """Результат выполнения команды."""

    success: bool  # Успешно ли выполнена команда
    command_type: str  # Тип команды (например, "StepCommand")
    reason: Optional[str] = None  # Причина неудачи, если команда не удалась
    step_result: Optional[StepResult] = None  # Результат шага, если команда была StepCommand


class SimulationEngine:
    """Основной движок симуляции экосистемы.

    Управляет всем процессом симуляции: агентами, миром, геномами,
    применением действий и обработкой команд.
    """

    def __init__(
        self,
        cfg: SimConfig,  # Конфигурация симуляции с параметрами
        world: WorldReadAPI,  # API для чтения состояния мира
        genome_updater: GenomeUpdater,  # Обновлятор состояний геномов
        child_genome_builder: ChildGenomeBuilder,  # Компонент для создания генома ребенка
        genome_effects_resolver: GenomeEffectsResolver,  # Компонент для разрешения эффектов генов
        seed: int = 0,  # Seed для генератора случайных чисел
    ) -> None:
        self.cfg = cfg  # Конфигурация симуляции
        self.world = world  # Доступ к миру
        self.genome_updater = genome_updater  # Обновлятор геномов
        self.child_genome_builder = child_genome_builder  # Компонент для создания генома ребенка
        self.genome_effects_resolver = genome_effects_resolver  # Компонент для разрешения эффектов
        self.rng = random.Random(seed)  # Генератор случайных чисел
        self.tick: Tick = Tick(0)  # Текущий тик симуляции
        self.agents = AgentRegistry()  # Реестр всех агентов
        self.applier = ActionApplier()  # Применятель действий
        self.conflict_resolver = ConflictResolver()

    def add_agent(self, agent: Agent) -> None:
        agent.state.validate(self.cfg)
        self.agents.add(agent)

    def build_observation(self, agent: Agent) -> Observation:
        """Строит наблюдение для агента на основе текущего состояния мира.

        Собирает информацию о текущей территории, других агентах на ней
        и соседних территориях.
        """
        current_id = agent.state.location

        individuals_here = [
            other.state.id
            for other in self.agents.all()
            if other.state.location == current_id and other.state.id != agent.state.id
        ]

        neighbor_territories = [edge.to for edge in self.world.graph().neighbors(current_id)]

        return Observation(
            current_id=current_id,
            individuals_here=individuals_here,
            neighbor_territories=neighbor_territories,
        )

    def update_agent_genome(self, agent: Agent) -> None:
        """Обновляет состояние генома агента на основе текущего контекста.

        Использует genome_updater для перехода генома в новое состояние
        в зависимости от территории и мира.
        """
        context = GenomeContext(
            territory_id=agent.state.location,
        )

        agent.genome_state = self.genome_updater.next_state(
            genome=agent.genome,
            current_state=agent.genome_state,
            context=context,
            world=self.world,
        )

    def apply_tick_hunger(
        self,
        applied_results: list[AppliedActionResult],
    ) -> None:
        """Применяет голод за тик ко всем агентам, которые не поели успешно.

        Увеличивает уровень голода у агентов, чьи действия по поеданию еды
        не увенчались успехом.
        """
        ate_successfully = {
            result.agent_id for result in applied_results if result.consumed_food and result.success
        }

        for agent in self.agents.all():
            if str(agent.state.id) not in ate_successfully:
                agent.state.increase_hunger(1, self.cfg)

    def regenerate_territories(self) -> None:
        """Регенерирует еду на всех территориях мира."""
        for territory in self.world.all_territories():
            territory.regenerate_food()

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

            agents.append(
                AgentDTO(
                    id=agent.state.id,
                    location=agent.state.location,
                    hunger=agent.state.hunger,
                    hp=agent.state.hp,
                    base_strength=agent.state.base_strength,
                    effective_strength=effective_strength,
                    base_defense=agent.state.base_defense,
                    effective_defense=effective_defense,
                    sex=agent.state.sex,
                    pregnant=agent.state.pregnant,
                    ticks_to_birth=agent.state.ticks_to_birth,
                    father_id=agent.state.father_id,
                    base_temp_pref=agent.state.base_temp_pref,
                    effective_temp_pref=effective_temp_pref,
                    satisfaction=agent.state.satisfaction,
                    alive=agent.state.alive,
                    active_genes=active_genes,
                )
            )

        return agents

    def get_state(self) -> SimulationStateDTO:
        """Получает текущее состояние всей симуляции."""
        return SimulationStateDTO(
            tick=int(self.tick),
            territories=self.build_territory_dtos(),
            agents=self.build_agent_dtos(),
        )

    def step(self) -> StepResult:
        decisions: List[Decision] = []
        applied_results: List[AppliedActionResult] = []
        fights: list[FightEvent] = []

        decisions_buffer: list[tuple[Agent, ActionOption, PhenotypeSnapshot]] = []

        # 1. Решения агентов
        for agent in self.agents.all():
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

        # 2. Сначала применяем не-EAT действия
        eat_claims_by_territory: dict[str, list[tuple[Agent, PhenotypeSnapshot]]] = defaultdict(
            list
        )

        for agent, action, phenotype in decisions_buffer:
            if action.type.value == "eat":
                eat_claims_by_territory[str(agent.state.location)].append((agent, phenotype))
                continue

            result = self.applier.apply(
                agent=agent,
                action=action,
                world=self.world,
                agents=self.agents,
                cfg=self.cfg,
            )
            applied_results.append(result)

        # 3. Потом отдельно разрешаем EAT-конфликты
        for territory_id, contenders in eat_claims_by_territory.items():
            if len(contenders) == 1:
                winner = contenders[0][0]
                result = self.applier.apply_successful_eat(
                    agent=winner,
                    world=self.world,
                    cfg=self.cfg,
                )
                applied_results.append(result)
                continue

            winner, fight_results = self.conflict_resolver.resolve_food_conflict(
                territory_id=territory_id,
                contenders=contenders,
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

        # 4. Обновление голода
        self.apply_tick_hunger(applied_results)

        # 5. Регенерация еды
        self.regenerate_territories()

        # 6. Рождения
        births = self.resolve_births()

        # 7. Смерти от голода
        starvation_deaths = self.apply_starvation_damage()

        # 7. Смерти от боев
        combat_deaths = self.resolve_hp_deaths()

        deaths = combat_deaths + starvation_deaths

        result = StepResult(
            tick=self.tick,
            decisions=decisions,
            applied_results=applied_results,
            deaths=deaths,
            births=births,
            fights=fights,
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
        """Обрабатывает список команд симуляции."""
        results: list[CommandResult] = []
        for command in commands:
            results.append(self.handle_command(command))
        return results

    def _generate_child_id(self) -> IndividualId:
        return IndividualId(f"child_{int(self.tick)}_{self.rng.randint(1000, 9999)}")

    def resolve_births(self) -> list[BirthResult]:
        """Обрабатывает рождения новых агентов.

        Проверяет беременных агентов, уменьшает счетчик до рождения,
        и создает новых агентов при достижении 0.
        """
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
                base_temp_pref=child_temp_pref,
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
                    child_id=child_id,
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
                id="g_hunger_drive",
                name="Hunger drive",
                chromosome_id="chr1",
                position=1.0,
                threshold=0.2,
            )
        )
        genome.add_gene(
            Gene(
                id="g_risk_move",
                name="Risk movement",
                chromosome_id="chr1",
                position=2.0,
                threshold=0.0,
            )
        )
        genome.add_gene(
            Gene(
                id="g_low_activity",
                name="Low activity",
                chromosome_id="chr1",
                position=3.0,
                threshold=0.3,
            )
        )
        genome.add_gene(
            Gene(
                id="g_heat_resistance",
                name="Heat resistance",
                chromosome_id="chr2",
                position=1.0,
                threshold=0.0,
            )
        )
        genome.add_gene(
            Gene(
                id="g_cold_resistance",
                name="Cold resistance",
                chromosome_id="chr2",
                position=2.0,
                threshold=0.0,
            )
        )
        genome.add_gene(
            Gene(
                id="g_reproduction_drive",
                name="Reproduction drive",
                chromosome_id="chr2",
                position=3.0,
                threshold=0.1,
            )
        )

        genome.add_edge(
            GeneEdge(
                source_gene_id="g_hunger_drive",
                target_gene_id="g_risk_move",
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
            if agent.state.hunger >= self.cfg.hunger_max:
                agent.state.decrease_hp(1, self.cfg)

            if not agent.state.alive or agent.state.hp <= self.cfg.hp_min:
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
            self.agents.remove(agent_id)

        return deaths
