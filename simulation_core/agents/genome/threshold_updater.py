from dataclasses import dataclass

from simulation_core.agents.genome.genome import Genome
from simulation_core.agents.genome.state import GenomeState
from simulation_core.agents.genome.updater import GenomeContext, GenomeUpdater
from simulation_core.world.api import WorldReadAPI


@dataclass(frozen=True)
class ThresholdGenomeUpdater(GenomeUpdater):
    """Обновляет состояние генома на основе пороговой модели активации.
    Для каждого гена:
    1. Суммирует веса от всех активных входящих генов
    2. Добавляет внешний сигнал от среды (температура)
    3. Активирует ген, если суммарный вход >= порога гена
    """

    def next_state(
        self,
        genome: Genome,  # Геном агента
        current_state: GenomeState,  # Текущее состояние генома
        context: GenomeContext,  # Контекст (территория)
        world: WorldReadAPI,  # Мир
    ) -> GenomeState:
        """Вычисляет следующее состояние генома."""
        territory = world.get_territory(context.territory_id)
        next_state = GenomeState()

        for gene in genome.all_genes():
            total_input = 0.0

            # 1. вклад входящих активных генов
            for edge in genome.incoming_edges(gene.id):
                if current_state.is_active(edge.source_gene_id):
                    total_input += edge.weight

            # 2. вклад среды
            total_input += self._environment_signal(
                gene_id=gene.id,
                temperature=territory.temperature,
            )

            # 3. пороговая активация
            is_active = total_input >= gene.threshold
            next_state.set_active(gene.id, is_active)

        return next_state

    def _environment_signal(self, gene_id: str, temperature: float) -> float:
        """Вычисляет внешний сигнал от среды для гена.

        Использует простое правило на основе ID гена:
        - heat-гены активируются при высокой температуре
        - cold-гены активируются при низкой температуре
        - остальные гены не получают внешнего сигнала
        """
        gene_id_lower = gene_id.lower()

        if "heat" in gene_id_lower:
            # чем выше температура, тем сильнее активация heat-генов
            return temperature / 10.0

        if "cold" in gene_id_lower:
            # чем ниже температура, тем сильнее активация cold-генов
            return (30.0 - temperature) / 10.0

        return 0.0
