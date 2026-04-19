from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateGeneDefinition:
    key: str
    name: str
    effect_type: str
    threshold: float
    weight: float
    x: float
    y: float
    default_active: bool = True


@dataclass(frozen=True)
class TemplateGenomeDefinition:
    key: str
    name: str
    description: str
    genes: tuple[TemplateGeneDefinition, ...]
    edges: tuple[tuple[str, str, float], ...] = ()


@dataclass(frozen=True)
class TerritoryDefinition:
    key: str
    food: float
    food_capacity: float
    food_regen_per_tick: float
    temperature: float
    x: float
    y: float


@dataclass(frozen=True)
class AgentGroupDefinition:
    genome_key: str
    territory_key: str
    count: int
    sex_pattern: tuple[str, ...] = ("female", "male")
    hunger: float = 1.5
    hp: float = 5.0
    strength: float = 1.0
    defense: float = 1.0
    temp_pref: float = 20.0
    satisfaction: float = 3.0


@dataclass(frozen=True)
class ScenarioDefinition:
    key: str
    name: str
    description: str
    territories: tuple[TerritoryDefinition, ...]
    edges: tuple[tuple[str, str, float], ...]
    agent_groups: tuple[AgentGroupDefinition, ...]


TEMPLATE_GENOMES: tuple[TemplateGenomeDefinition, ...] = (
    TemplateGenomeDefinition(
        key="balanced_grazer",
        name="Шаблон: сбалансированный травоядный",
        description=(
            "Базовый всеядный/травоядный агент для контрольных прогонов: умеренная "
            "выживаемость, нормальное размножение и невысокая агрессия."
        ),
        genes=(
            TemplateGeneDefinition("hp", "Умеренное здоровье", "MAX_HP", 0, 1.05, 120, 80),
            TemplateGeneDefinition("defense", "Осторожная защита", "DEFENSE", 0, 1.1, 260, 80),
            TemplateGeneDefinition("hunger", "Пищевой драйв", "HUNGER_DRIVE", 3.0, 1.15, 80, 210),
            TemplateGeneDefinition(
                "repro", "Умеренное размножение", "REPRODUCTION_DRIVE", 3.0, 1.0, 230, 220
            ),
            TemplateGeneDefinition(
                "site", "Привязанность к месту", "SITE_FIDELITY", 3.0, 1.05, 370, 210
            ),
            TemplateGeneDefinition(
                "social", "Нормальная социальность", "SOCIAL_TOLERANCE", 4.0, 0.8, 260, 340
            ),
        ),
        edges=(("defense", "site", 1.08), ("hunger", "repro", 0.92)),
    ),
    TemplateGenomeDefinition(
        key="heat_migrant",
        name="Шаблон: теплолюбивый мигрант",
        description=(
            "Агент для жарких и нестабильных карт: хорошо переносит высокую температуру "
            "и чаще уходит с неподходящих территорий."
        ),
        genes=(
            TemplateGeneDefinition(
                "heat", "Теплоустойчивость", "HEAT_RESISTANCE", 26.0, 1.4, 100, 90
            ),
            TemplateGeneDefinition(
                "dispersal", "Поиск новых мест", "DISPERSAL_DRIVE", 2.5, 1.35, 260, 90
            ),
            TemplateGeneDefinition(
                "hunger", "Быстрый поиск пищи", "HUNGER_DRIVE", 2.5, 1.2, 80, 240
            ),
            TemplateGeneDefinition(
                "repro", "Размножение при комфорте", "REPRODUCTION_DRIVE", 3.2, 0.95, 260, 240
            ),
            TemplateGeneDefinition("metabolism", "Экономный обмен", "METABOLISM", 0, 0.9, 420, 160),
        ),
        edges=(("heat", "dispersal", 1.15), ("metabolism", "hunger", 0.9)),
    ),
    TemplateGenomeDefinition(
        key="cold_social",
        name="Шаблон: холодоустойчивый стайный",
        description=(
            "Хорошо держится в холодных областях и меньше страдает от плотности. "
            "Полезен для проверки перенаселения и температурного отбора."
        ),
        genes=(
            TemplateGeneDefinition(
                "cold", "Холодоустойчивость", "COLD_RESISTANCE", 12.0, 1.45, 100, 90
            ),
            TemplateGeneDefinition(
                "social", "Стайная терпимость", "SOCIAL_TOLERANCE", 3.0, 1.5, 260, 90
            ),
            TemplateGeneDefinition("defense", "Групповая защита", "DEFENSE", 0, 1.15, 420, 90),
            TemplateGeneDefinition("site", "Оседлость", "SITE_FIDELITY", 3.0, 1.25, 180, 250),
            TemplateGeneDefinition(
                "repro", "Стабильное размножение", "REPRODUCTION_DRIVE", 3.3, 0.95, 350, 250
            ),
        ),
        edges=(("social", "site", 1.18), ("cold", "defense", 1.08)),
    ),
    TemplateGenomeDefinition(
        key="predator",
        name="Шаблон: хищник",
        description=(
            "Сильный, более агрессивный агент с выгодой от успешной охоты. Нужен для "
            "сценариев хищник-жертва и конфликтов за ресурсы."
        ),
        genes=(
            TemplateGeneDefinition("strength", "Сила охотника", "STRENGTH", 0, 1.55, 100, 80),
            TemplateGeneDefinition("hp", "Крепкое тело", "MAX_HP", 0, 1.2, 260, 80),
            TemplateGeneDefinition(
                "predation", "Охотничий драйв", "PREDATION_DRIVE", 2.5, 1.6, 80, 230
            ),
            TemplateGeneDefinition(
                "digestion", "Хищное пищеварение", "CARNIVORE_DIGESTION", 2.5, 1.45, 260, 230
            ),
            TemplateGeneDefinition(
                "aggression", "Ресурсная агрессия", "AGGRESSION_DRIVE", 4.0, 1.25, 420, 230
            ),
        ),
        edges=(("strength", "predation", 1.2), ("digestion", "predation", 1.1)),
    ),
    TemplateGenomeDefinition(
        key="mutable_pioneer",
        name="Шаблон: изменчивый пионер",
        description=(
            "Быстро расселяется и чаще мутирует у потомства. Хорош для экспериментов "
            "с бутылочным горлышком, адаптацией и разнообразием геномов."
        ),
        genes=(
            TemplateGeneDefinition(
                "mutation", "Высокая изменчивость", "MUTATION_RATE", 0, 2.2, 100, 80
            ),
            TemplateGeneDefinition(
                "dispersal", "Пионерское расселение", "DISPERSAL_DRIVE", 2.8, 1.45, 260, 80
            ),
            TemplateGeneDefinition(
                "repro", "Быстрое размножение", "REPRODUCTION_DRIVE", 2.8, 1.35, 100, 240
            ),
            TemplateGeneDefinition(
                "hunger", "Рискованный поиск пищи", "HUNGER_DRIVE", 3.0, 1.25, 260, 240
            ),
            TemplateGeneDefinition("defense", "Хрупкая защита", "DEFENSE", 0, 0.85, 420, 160),
        ),
        edges=(("mutation", "repro", 1.12), ("dispersal", "hunger", 1.08)),
    ),
)


SCENARIOS: tuple[ScenarioDefinition, ...] = (
    ScenarioDefinition(
        key="baseline_mosaic",
        name="Сценарий: равновесная мозаика",
        description=(
            "Контрольная карта с разной пищей и умеренными температурами. Помогает "
            "сравнивать новые изменения движка с предсказуемой базовой динамикой."
        ),
        territories=(
            TerritoryDefinition("meadow", 18, 24, 2.0, 20, 120, 120),
            TerritoryDefinition("grove", 14, 18, 1.6, 17, 380, 140),
            TerritoryDefinition("hill", 8, 12, 0.9, 14, 220, 360),
            TerritoryDefinition("pond", 22, 28, 2.4, 23, 540, 340),
        ),
        edges=(
            ("meadow", "grove", 1.0),
            ("grove", "hill", 1.4),
            ("meadow", "hill", 1.2),
            ("grove", "pond", 0.9),
            ("hill", "pond", 1.6),
        ),
        agent_groups=(
            AgentGroupDefinition("balanced_grazer", "meadow", 5, temp_pref=20),
            AgentGroupDefinition("balanced_grazer", "grove", 3, temp_pref=18),
            AgentGroupDefinition("predator", "hill", 2, hunger=2.5, strength=1.2),
        ),
    ),
    ScenarioDefinition(
        key="climate_gradient",
        name="Сценарий: климатический градиент",
        description=(
            "Линейка холодных, умеренных и жарких территорий. Видно, какие геномы "
            "закрепляются в подходящей температурной нише."
        ),
        territories=(
            TerritoryDefinition("tundra", 10, 16, 1.4, 6, 80, 280),
            TerritoryDefinition("forest", 18, 24, 2.0, 18, 300, 280),
            TerritoryDefinition("savanna", 16, 22, 1.8, 29, 520, 280),
            TerritoryDefinition("desert", 6, 10, 0.8, 36, 740, 280),
        ),
        edges=(
            ("tundra", "forest", 1.0),
            ("forest", "savanna", 1.0),
            ("savanna", "desert", 1.2),
        ),
        agent_groups=(
            AgentGroupDefinition("cold_social", "tundra", 4, temp_pref=10),
            AgentGroupDefinition("balanced_grazer", "forest", 4, temp_pref=20),
            AgentGroupDefinition("heat_migrant", "savanna", 4, temp_pref=28),
            AgentGroupDefinition("heat_migrant", "desert", 2, hunger=2.5, temp_pref=32),
        ),
    ),
    ScenarioDefinition(
        key="predator_prey",
        name="Сценарий: хищник и жертва",
        description=(
            "Много травоядных, меньше хищников и карта с убежищами. Подходит для "
            "анализа циклов охоты, смертности и восстановления популяции."
        ),
        territories=(
            TerritoryDefinition("pasture", 30, 36, 2.8, 21, 140, 180),
            TerritoryDefinition("shelter", 18, 24, 1.6, 19, 420, 120),
            TerritoryDefinition("den", 8, 12, 0.8, 16, 420, 390),
            TerritoryDefinition("river", 24, 30, 2.3, 22, 690, 250),
        ),
        edges=(
            ("pasture", "shelter", 0.8),
            ("shelter", "den", 1.2),
            ("pasture", "den", 1.5),
            ("shelter", "river", 1.0),
            ("den", "river", 1.3),
        ),
        agent_groups=(
            AgentGroupDefinition("balanced_grazer", "pasture", 8, temp_pref=20),
            AgentGroupDefinition("cold_social", "shelter", 4, temp_pref=18),
            AgentGroupDefinition("predator", "den", 3, hunger=3.0, strength=1.25),
        ),
    ),
    ScenarioDefinition(
        key="overcrowding",
        name="Сценарий: перенаселение",
        description=(
            "Одна богатая центральная территория и бедные окраины. Сравнивает "
            "социальную терпимость, расселение и конфликты при высокой плотности."
        ),
        territories=(
            TerritoryDefinition("center", 34, 40, 2.4, 20, 370, 260),
            TerritoryDefinition("north", 8, 12, 1.0, 14, 370, 70),
            TerritoryDefinition("east", 8, 12, 1.0, 25, 650, 260),
            TerritoryDefinition("south", 8, 12, 1.0, 28, 370, 460),
            TerritoryDefinition("west", 8, 12, 1.0, 11, 90, 260),
        ),
        edges=(
            ("center", "north", 1.0),
            ("center", "east", 1.0),
            ("center", "south", 1.0),
            ("center", "west", 1.0),
        ),
        agent_groups=(
            AgentGroupDefinition("cold_social", "center", 6, temp_pref=18),
            AgentGroupDefinition("heat_migrant", "center", 6, temp_pref=24),
            AgentGroupDefinition("balanced_grazer", "center", 4, temp_pref=20),
        ),
    ),
    ScenarioDefinition(
        key="mutation_bottleneck",
        name="Сценарий: мутационное бутылочное горлышко",
        description=(
            "Мало еды, несколько островков и изменчивые пионеры. Нужен для наблюдения "
            "за тем, помогает ли высокий MUTATION_RATE быстрее найти устойчивую стратегию."
        ),
        territories=(
            TerritoryDefinition("start", 10, 14, 1.0, 20, 100, 260),
            TerritoryDefinition("cold_island", 6, 10, 0.8, 8, 330, 110),
            TerritoryDefinition("hot_island", 6, 10, 0.8, 34, 330, 410),
            TerritoryDefinition("oasis", 18, 22, 1.7, 23, 620, 260),
        ),
        edges=(
            ("start", "cold_island", 1.4),
            ("start", "hot_island", 1.4),
            ("cold_island", "oasis", 1.6),
            ("hot_island", "oasis", 1.6),
            ("start", "oasis", 2.2),
        ),
        agent_groups=(
            AgentGroupDefinition("mutable_pioneer", "start", 6, hunger=2.0, temp_pref=21),
            AgentGroupDefinition("balanced_grazer", "start", 4, hunger=2.0, temp_pref=20),
        ),
    ),
)
