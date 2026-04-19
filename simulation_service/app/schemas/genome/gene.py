from pydantic import BaseModel


class RuntimeGene(BaseModel):
    id: int
    name: str
    effect_type: str
    threshold: float
    weight: float = 1.0
    default_active: bool = False
