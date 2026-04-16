from app.enums import GeneEffectType

from ..base import Node


class Gene(Node):
    """Gene node in genome"""

    effect_type: GeneEffectType
    threshold: float
    is_active: bool

    class Config:
        from_attributes = True
