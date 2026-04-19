from enum import Enum


class AgentSex(str, Enum):
    MALE = "male"
    FEMALE = "female"


class SimulationStatus(str, Enum):
    DRAFT = "draft"
    LOADED = "loaded"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class AgentActionType(str, Enum):
    EAT = "eat"
    MOVE = "move"
    MATE = "mate"
    REST = "rest"
    HUNT = "hunt"


class GeneEffectType(str, Enum):
    MAX_HP = "MAX_HP"
    STRENGTH = "STRENGTH"
    DEFENSE = "DEFENSE"
    METABOLISM = "METABOLISM"
    HUNGER_DRIVE = "HUNGER_DRIVE"
    DISPERSAL_DRIVE = "DISPERSAL_DRIVE"
    SITE_FIDELITY = "SITE_FIDELITY"
    REPRODUCTION_DRIVE = "REPRODUCTION_DRIVE"
    HEAT_RESISTANCE = "HEAT_RESISTANCE"
    COLD_RESISTANCE = "COLD_RESISTANCE"
    AGGRESSION_DRIVE = "AGGRESSION_DRIVE"
    PREDATION_DRIVE = "PREDATION_DRIVE"
    CARNIVORE_DIGESTION = "CARNIVORE_DIGESTION"
    CANNIBAL_TOLERANCE = "CANNIBAL_TOLERANCE"
    SOCIAL_TOLERANCE = "SOCIAL_TOLERANCE"
