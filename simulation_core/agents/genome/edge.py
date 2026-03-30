from dataclasses import dataclass


@dataclass(frozen=True)
class GeneEdge:
    """Ориентированная связь между двумя генами в графе генома"""

    source_gene_id: int  # ID исходного гена (отправитель влияния)
    target_gene_id: int  # ID целевого гена (получатель влияния)
    weight: float  # Вес связи (положительный = активация, отрицательный = подавление)
