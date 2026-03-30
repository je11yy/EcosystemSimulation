from dataclasses import dataclass, field


@dataclass
class GenomeState:
    """Текущее состояние активности генов в геноме агента.

    Хранит информацию о том, какие гены активны на текущий момент времени.
    Состояние генов обновляется на каждом тике симуляции на основе
    входных сигналов и связей между генами.
    """

    gene_activity: dict[int, bool] = field(default_factory=lambda: {})  # gene_id -> активен ли ген

    def is_active(self, gene_id: int) -> bool:
        return self.gene_activity.get(gene_id, False)

    def set_active(self, gene_id: int, value: bool) -> None:
        self.gene_activity[gene_id] = value

    def copy(self) -> "GenomeState":
        return GenomeState(gene_activity=dict(self.gene_activity))
