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
    HUNGER = "hunger"
    HP = "hp"
    STRENGTH = "strength"
    DEFENSE = "defense"
    TEMP_PREF = "temp_pref"
    SATISFACTION = "satisfaction"
    HUNT_COOLDOWN = "hunt_cooldown"
