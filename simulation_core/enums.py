from enum import Enum


class AgentSex(str, Enum):
    MALE = "male"
    FEMALE = "female"


class AgentActionType(str, Enum):
    EAT = "eat"
    MOVE = "move"
    MATE = "mate"
    REST = "rest"
    HUNT = "hunt"
