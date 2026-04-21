from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, init=False)
class GeneEdge:
    source_id: int
    target_id: int
    weight: float

    def __init__(
        self,
        source_id: Optional[int] = None,
        target_id: Optional[int] = None,
        weight: float = 1.0,
        source_gene_id: Optional[int] = None,
        target_gene_id: Optional[int] = None,
    ):
        resolved_source_id = source_id if source_id is not None else source_gene_id
        resolved_target_id = target_id if target_id is not None else target_gene_id
        if resolved_source_id is None:
            raise ValueError("GeneEdge source_id is required")
        if resolved_target_id is None:
            raise ValueError("GeneEdge target_id is required")

        object.__setattr__(self, "source_id", resolved_source_id)
        object.__setattr__(self, "target_id", resolved_target_id)
        object.__setattr__(self, "weight", weight)

    @property
    def source_gene_id(self) -> int:
        return self.source_id

    @property
    def target_gene_id(self) -> int:
        return self.target_id
