from pydantic import BaseModel, Field

from app.enums import GeneEffectType

from ..base import Node, Position


class GeneCreate(BaseModel):
    name: str
    effect_type: GeneEffectType
    threshold: float = Field(
        default=0.0,
        description="Порог активации: условие, после которого ген начинает работать.",
    )
    weight: float = Field(
        default=1.0,
        ge=0,
        description="Сила гена: множитель статов или вес поведения.",
    )
    position: Position
    default_active: bool = True


class Gene(Node):
    name: str
    effect_type: GeneEffectType
    weight: float
    threshold: float
    default_active: bool

    class Config:
        from_attributes = True
