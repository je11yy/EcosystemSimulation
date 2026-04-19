from dataclasses import dataclass, field

from ..config import SimConfig
from ..enums import AgentSex
from ..genome.models import Genome
from ..utils import clamp
from .phenotype import AgentPhenotype, build_agent_phenotype
from .traits import TraitAggregator, TraitVector


@dataclass
class AgentState:
    id: int
    sex: AgentSex
    hunger: float
    hp: float
    is_pregnant: bool
    ticks_to_birth: int
    satisfaction: float
    hunt_cooldown: int
    base_strength: float
    base_defense: float
    base_temp_pref: float
    location: int
    is_alive: bool = True
    phenotype: AgentPhenotype = field(init=False)
    traits: TraitVector = field(init=False)

    def __post_init__(self) -> None:
        self.phenotype = AgentPhenotype(
            max_hp=SimConfig().hp_max,
            strength=self.base_strength,
            defense=self.base_defense,
        )
        self.traits = TraitVector()

    @property
    def max_hp(self) -> float:
        return self.phenotype.max_hp

    @property
    def effective_strength(self) -> float:
        return self.phenotype.strength

    @property
    def effective_defense(self) -> float:
        return self.phenotype.defense

    def apply_gene_effects(self, genome: Genome, cfg: SimConfig) -> None:
        trait_aggregator = TraitAggregator(genome)
        self.phenotype = build_agent_phenotype(self, genome, cfg, trait_aggregator)
        self.traits = trait_aggregator.build_vector()
        self.validate(cfg)

    def validate(self, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger, cfg.hunger_min, cfg.hunger_max)
        self.hp = clamp(self.hp, cfg.hp_min, self.max_hp)
        self.base_strength = clamp(self.base_strength, cfg.strength_min, cfg.strength_max)
        self.base_defense = clamp(self.base_defense, cfg.defense_min, cfg.defense_max)

    def increase_hunger(self, amount: float, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger + amount, cfg.hunger_min, cfg.hunger_max)

    def decrease_hunger(self, amount: float, cfg: SimConfig) -> None:
        self.hunger = clamp(self.hunger - amount, cfg.hunger_min, cfg.hunger_max)

    def increase_hp(self, amount: float, cfg: SimConfig) -> None:
        self.hp = clamp(self.hp + amount, cfg.hp_min, self.max_hp)

    def decrease_hp(self, amount: float, cfg: SimConfig) -> None:
        self.hp = clamp(self.hp - amount, cfg.hp_min, self.max_hp)
        if self.hp <= cfg.hp_min:
            self.is_alive = False

    def move_to(self, territory_id: int) -> None:
        self.location = territory_id
