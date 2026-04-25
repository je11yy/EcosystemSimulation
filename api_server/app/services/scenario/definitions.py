from dataclasses import dataclass


@dataclass(frozen=True)
class TemplateGeneDefinition:
    key: str
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


def _bidirectional_edges(
    *edges: tuple[str, str, float],
) -> tuple[tuple[str, str, float], ...]:
    result: list[tuple[str, str, float]] = []
    for source, target, weight in edges:
        result.append((source, target, weight))
        result.append((target, source, weight))
    return tuple(result)


TEMPLATE_GENOMES: tuple[TemplateGenomeDefinition, ...] = (
    TemplateGenomeDefinition(
        key="balanced_grazer",
        name="Базовый травоядный",
        description=(
            "Геном с умеренными параметрами выживания, защиты, пищевого поиска, "
            "размножения и социальной устойчивости для контрольных симуляций."
        ),
        genes=(
            TemplateGeneDefinition("hp", "MAX_HP", 0, 1.05, 120, 80),
            TemplateGeneDefinition("defense", "DEFENSE", 0, 1.1, 260, 80),
            TemplateGeneDefinition("hunger", "HUNGER_DRIVE", 3.0, 1.15, 80, 210),
            TemplateGeneDefinition("repro", "REPRODUCTION_DRIVE", 3.0, 1.0, 230, 220),
            TemplateGeneDefinition("site", "SITE_FIDELITY", 3.0, 1.05, 370, 210),
            TemplateGeneDefinition("social", "SOCIAL_TOLERANCE", 4.0, 0.8, 260, 340),
        ),
        edges=(("defense", "site", 1.08), ("hunger", "repro", 0.92)),
    ),
    TemplateGenomeDefinition(
        key="heat_migrant",
        name="Термоустойчивый мигрант",
        description=(
            "Геном с повышенной устойчивостью к высокой температуре и выраженной "
            "склонностью к перемещению между территориями при ухудшении условий."
        ),
        genes=(
            TemplateGeneDefinition("heat", "HEAT_RESISTANCE", 26.0, 1.4, 100, 90),
            TemplateGeneDefinition("dispersal", "DISPERSAL_DRIVE", 2.5, 1.35, 260, 90),
            TemplateGeneDefinition("hunger", "HUNGER_DRIVE", 2.5, 1.2, 80, 240),
            TemplateGeneDefinition("repro", "REPRODUCTION_DRIVE", 3.2, 0.95, 260, 240),
            TemplateGeneDefinition("metabolism", "METABOLISM", 0, 0.9, 420, 160),
        ),
        edges=(("heat", "dispersal", 1.15), ("metabolism", "hunger", 0.9)),
    ),
    TemplateGenomeDefinition(
        key="cold_social",
        name="Холодоустойчивый социальный агент",
        description=(
            "Геном для холодных территорий с повышенной устойчивостью к низкой "
            "температуре и высокой плотности популяции."
        ),
        genes=(
            TemplateGeneDefinition("cold", "COLD_RESISTANCE", 12.0, 1.45, 100, 90),
            TemplateGeneDefinition("social", "SOCIAL_TOLERANCE", 3.0, 1.5, 260, 90),
            TemplateGeneDefinition("defense", "DEFENSE", 0, 1.15, 420, 90),
            TemplateGeneDefinition("site", "SITE_FIDELITY", 3.0, 1.25, 180, 250),
            TemplateGeneDefinition("repro", "REPRODUCTION_DRIVE", 3.3, 0.95, 350, 250),
        ),
        edges=(("social", "site", 1.18), ("cold", "defense", 1.08)),
    ),
    TemplateGenomeDefinition(
        key="predator",
        name="Хищник",
        description=(
            "Геном с усиленными параметрами силы, охоты, агрессии и усвоения добычи "
            "для сценариев ресурсного давления."
        ),
        genes=(
            TemplateGeneDefinition("strength", "STRENGTH", 0, 1.35, 100, 80),
            TemplateGeneDefinition("hp", "MAX_HP", 0, 1.1, 260, 80),
            TemplateGeneDefinition("predation", "PREDATION_DRIVE", 3.5, 1.25, 80, 230),
            TemplateGeneDefinition("digestion", "CARNIVORE_DIGESTION", 3.0, 1.15, 260, 230),
            TemplateGeneDefinition("aggression", "AGGRESSION_DRIVE", 4.5, 1.0, 420, 230),
        ),
        edges=(("strength", "predation", 1.08), ("digestion", "predation", 1.04)),
    ),
    TemplateGenomeDefinition(
        key="mutable_pioneer",
        name="Агент с повышенной изменчивостью",
        description=(
            "Геном с повышенной вероятностью мутаций, склонностью к расселению "
            "и ускоренному воспроизводству в нестабильной среде."
        ),
        genes=(
            TemplateGeneDefinition("mutation", "MUTATION_RATE", 0, 2.2, 100, 80),
            TemplateGeneDefinition("dispersal", "DISPERSAL_DRIVE", 2.8, 1.45, 260, 80),
            TemplateGeneDefinition("repro", "REPRODUCTION_DRIVE", 2.8, 1.35, 100, 240),
            TemplateGeneDefinition("hunger", "HUNGER_DRIVE", 3.0, 1.25, 260, 240),
            TemplateGeneDefinition("defense", "DEFENSE", 0, 0.85, 420, 160),
        ),
        edges=(("mutation", "repro", 1.12), ("dispersal", "hunger", 1.08)),
    ),
)


SCENARIOS: tuple[ScenarioDefinition, ...] = (
    ScenarioDefinition(
        key="baseline_mosaic",
        name="Базовый",
        description=(
            "Симуляция с 4 территориями умеренного температурного диапазона и "
            "агентами двух геномов: базового травоядного и хищника."
        ),
        territories=(
            TerritoryDefinition("meadow", 18, 24, 2.0, 20, 120, 120),
            TerritoryDefinition("grove", 14, 18, 1.6, 17, 380, 140),
            TerritoryDefinition("hill", 8, 12, 0.9, 14, 220, 360),
            TerritoryDefinition("pond", 22, 28, 2.4, 23, 540, 340),
        ),
        edges=(
            ("meadow", "grove", 1.0),
            ("grove", "meadow", 1.0),
            ("grove", "hill", 1.4),
            ("hill", "grove", 1.4),
            ("meadow", "hill", 1.2),
            ("hill", "meadow", 1.2),
            ("grove", "pond", 0.9),
            ("pond", "grove", 1.3),
            ("hill", "pond", 1.6),
            ("pond", "hill", 1.1),
        ),
        agent_groups=(
            AgentGroupDefinition("balanced_grazer", "meadow", 6, temp_pref=20),
            AgentGroupDefinition("balanced_grazer", "grove", 6, temp_pref=18),
            AgentGroupDefinition("balanced_grazer", "pond", 4, temp_pref=21),
            AgentGroupDefinition("predator", "hill", 4, hunger=2.8, strength=1.1),
        ),
    ),
    ScenarioDefinition(
        key="climate_gradient",
        name="Климатический градиент",
        description=(
            "Симуляция с 4 территориями, выстроенными по температурному градиенту, "
            "и агентами трех геномов: холодоустойчивого социального, базового "
            "травоядного и термоустойчивого мигранта."
        ),
        territories=(
            TerritoryDefinition("tundra", 10, 16, 1.4, 6, 80, 280),
            TerritoryDefinition("forest", 18, 24, 2.0, 18, 300, 280),
            TerritoryDefinition("savanna", 16, 22, 1.8, 29, 520, 280),
            TerritoryDefinition("desert", 6, 10, 0.8, 36, 740, 280),
        ),
        edges=_bidirectional_edges(
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
        name="Хищник-жертва",
        description=(
            "Симуляция с 4 территориями, повышенной кормовой базой для жертв и "
            "агентами трех геномов: базового травоядного, холодоустойчивого "
            "социального агента и хищника."
        ),
        territories=(
            TerritoryDefinition("pasture", 30, 36, 2.8, 21, 140, 180),
            TerritoryDefinition("shelter", 18, 24, 1.6, 19, 420, 120),
            TerritoryDefinition("den", 8, 12, 0.8, 16, 420, 390),
            TerritoryDefinition("river", 24, 30, 2.3, 22, 690, 250),
        ),
        edges=_bidirectional_edges(
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
        name="Перенаселение",
        description=(
            "Симуляция с 5 территориями, одной ресурсно насыщенной центральной зоной "
            "и агентами трех геномов: холодоустойчивого социального, "
            "термоустойчивого мигранта и базового травоядного."
        ),
        territories=(
            TerritoryDefinition("center", 34, 40, 2.4, 20, 370, 260),
            TerritoryDefinition("north", 8, 12, 1.0, 14, 370, 70),
            TerritoryDefinition("east", 8, 12, 1.0, 25, 650, 260),
            TerritoryDefinition("south", 8, 12, 1.0, 28, 370, 460),
            TerritoryDefinition("west", 8, 12, 1.0, 11, 90, 260),
        ),
        edges=_bidirectional_edges(
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
        name="Мутационное узкое место",
        description=(
            "Симуляция с 4 территориями, ограниченной кормовой базой и агентами "
            "двух геномов: агента с повышенной изменчивостью и базового травоядного."
        ),
        territories=(
            TerritoryDefinition("start", 10, 14, 1.0, 20, 100, 260),
            TerritoryDefinition("cold_island", 6, 10, 0.8, 8, 330, 110),
            TerritoryDefinition("hot_island", 6, 10, 0.8, 34, 330, 410),
            TerritoryDefinition("oasis", 18, 22, 1.7, 23, 620, 260),
        ),
        edges=(
            ("start", "cold_island", 1.4),
            ("cold_island", "start", 1.4),
            ("start", "hot_island", 1.4),
            ("hot_island", "start", 1.4),
            ("cold_island", "oasis", 1.6),
            ("oasis", "cold_island", 1.2),
            ("hot_island", "oasis", 1.6),
            ("oasis", "hot_island", 1.9),
            ("start", "oasis", 2.2),
            ("oasis", "start", 2.2),
        ),
        agent_groups=(
            AgentGroupDefinition("mutable_pioneer", "start", 6, hunger=2.0, temp_pref=21),
            AgentGroupDefinition("balanced_grazer", "start", 4, hunger=2.0, temp_pref=20),
        ),
    ),
)


TEMPLATE_GENOMES_BY_KEY = {definition.key: definition for definition in TEMPLATE_GENOMES}
TEMPLATE_GENOME_KEYS_BY_NAME = {definition.name: definition.key for definition in TEMPLATE_GENOMES}
