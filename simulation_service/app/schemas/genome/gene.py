from pydantic import BaseModel


class RuntimeGene(BaseModel):
    id: int
    effect_type: str
    x: float = 0.0
    y: float = 0.0
    threshold: float
    weight: float = 1.0
    default_active: bool = False
